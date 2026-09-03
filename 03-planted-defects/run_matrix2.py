# RECONSTRUCTED 2026-09-03 from the session record (see run_matrix.py header). Pass 2, P7-P20,
# byte-identical to the edits applied on 2026-09-02; results in matrix2-run.log. The six escapes
# (P8, P11, P13, P14, P15, P18) were independently reproduced by the maintainers (issue #489).
import subprocess, time, os
TGT="<WORKDIR>/verify-005-target"; POETRY=os.path.expanduser("~/.venv-poetry/bin/poetry"); os.chdir(TGT)
PLANTS=[
 ("P7","T2","src/grpc/client.py","    return BatchResult(\n        success=False,\n        status=AckStatus.ACK_STATUS_RETRYABLE_FAILURE,","    return BatchResult(\n        success=True,\n        status=AckStatus.ACK_STATUS_RETRYABLE_FAILURE,","no-ack send reported successful"),
 ("P8","T1*","src/grpc/cursor.py","        if a_val is None:\n            return -1","        if a_val is None:\n            return 1","record missing tie-breaker wins boundary [HINT-EXPOSED]"),
 ("P9","T4","src/state/store.py",'        if not isinstance(raw, str):\n            raise ValueError(f"malformed tagged cursor value {value!r}")','        if not isinstance(raw, str):\n            return raw',"malformed tag passes through"),
 ("P10","T5","cdk/cdk/record_identity.py","    canonical = json.dumps(basis, sort_keys=True, default=str)","    canonical = json.dumps(basis, sort_keys=False, default=str)","digest key-order dependent"),
 ("P11","T2","src/engine/stream_processor.py","            if self._is_truncate_insert():","            if False and self._is_truncate_insert():","truncate_insert resumes from persisted cursor (#307)"),
 ("P12","T6","src/runtime_archive.py",'REQUIRED_FILES = ("pipelines/manifest.json",)',"REQUIRED_FILES = ()","manifest-less archive accepted"),
 ("P13","T3","src/state/dead_letter_queue.py","        if written_count < len(batch):","        if written_count < 0:","batch DLQ loss no longer logged critical"),
 ("P14","T6","src/config/endpoint_resolver.py","    if ref.endpoint_id is None:\n        raise ConfigValidationError(","    if ref.endpoint_id is not None and False:\n        raise ConfigValidationError(","ref with no endpoint_id accepted"),
 ("P15","T1*","src/grpc/cursor.py","    if isinstance(a, str) and isinstance(b, str):","    if False and isinstance(a, str) and isinstance(b, str):","datetime strings compared lexically [HINT-EXPOSED]"),
 ("P16","T4","src/state/dead_letter_queue.py","        if isinstance(obj, Decimal):\n            return str(obj)","        if isinstance(obj, Decimal):\n            return float(obj)","DLQ record narrows Decimal to float"),
 ("P17","T4*","src/state/store.py",'    if isinstance(value, Decimal):\n        return {_TYPE_KEY: "decimal", _VALUE_KEY: str(value)}','    if isinstance(value, Decimal):\n        return float(value)',"Decimal cursor flattened to float [HINT-EXPOSED]"),
 ("P18","T6","src/destination/server.py","            if not schema_msg.ack_timeout_seconds:","            if False:","handshake without ack budget accepted (#234 guard)"),
 ("P19","T3","src/state/dead_letter_queue.py",'                                    and record.get("pipeline_id") != pipeline_id','                                    and record.get("pipeline_id") == pipeline_id',"DLQ review filter inverted"),
 ("P20","T5","cdk/cdk/base_handler.py","        reason = self.not_ready_reason(stream_id)  # skipcq: PYL-E1128\n        if reason is not None:","        reason = self.not_ready_reason(stream_id)  # skipcq: PYL-E1128\n        if reason is not None and False:","not-ready sink no longer rejects"),
]
def run_suite():
    t=time.time(); r=subprocess.run([POETRY,"run","pytest","-p","no:cacheprovider","-x","-q","--no-header"],capture_output=True,text=True,timeout=400)
    return r.returncode,(r.stdout+r.stderr),time.time()-t
for pid,inv,f,old,new,note in PLANTS:
    src=open(f).read(); n=src.count(old)
    if n!=1: print(f"{pid} PLANT-ERROR anchor n={n} :: {note}",flush=True); continue
    open(f,"w").write(src.replace(old,new,1))
    try: rc,out,dt=run_suite()
    finally: subprocess.run(["git","checkout","--",f],cwd=TGT)
    v="ESCAPED" if rc==0 else "CAUGHT" if rc==1 else f"PLANT-ERROR(rc={rc})"
    print(f"{pid} {inv:4} {v:8} {dt:5.0f}s :: {note}",flush=True)
