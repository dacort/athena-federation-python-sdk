from typing import Dict, List

import pyarrow as pa
from smart_open import open

SPILL_THRESHOLD_BYTES = 5 * 1024 * 1024  # 5MB


class BatchWriter:
    """
    BatchWriter provides an interface to stream PyArrow records to a RecordBatch.

    If the Batch gets too big (>6mb), it will automatically get written to S3.
    If not, the data is returned directly to the Lambda function.
    """

    def __init__(self, spill_config: Dict, schema: pa.Schema) -> None:
        self._spill_config = spill_config
        self._schema = schema
        self._spilled = False
        self._sink = pa.BufferOutputStream()
        self._writer = pa.RecordBatchStreamWriter(self._sink, self._schema)
        self._batch_size = 0

    @property
    def spilled(self) -> bool:
        return self._spilled

    def write_rows(self, data: Dict):
        record_batch = pa.RecordBatch.from_arrays(
            [pa.array(data[name]) for name in self._schema.names],
            schema=self._schema,
        )
        self._batch_size += record_batch.nbytes
        self._writer.write_batch(record_batch)

    def _build_spill_uri(self):
        return (
            f"s3://{self._spill_config['bucket']}/{self._spill_config['key']}/spill.0"
        )

    def close(self):
        print(f"Total bytes: {self._batch_size}")
        self._writer.close()
        # For now, if we're over 5mb of data, spill everything to s3.
        # I don't know how to do this without just serializing the whole thing.
        # If I use `RecordBatchStreamWriter`, it adds a schema IPC message when it doesn't need it.
        # Perhaps upgrading Arrow will help, but for now...let's do this.
        if self._batch_size > SPILL_THRESHOLD_BYTES:
            self._spilled = True
            with open(self._build_spill_uri(), "wb") as fout:
                fout.write(self.all_records().serialize())

    def all_records(self):
        buf = self._sink.getvalue()
        reader = pa.ipc.open_stream(buf)
        record_batches = [b for b in reader]
        one_chunk_table = pa.Table.from_batches(record_batches).combine_chunks()
        batches = one_chunk_table.to_batches(max_chunksize=None)
        return batches[0]