# RECONSTRUCTED 2026-09-03 from the session record: the scratchpad copy that ran on 2026-09-02
# was lost with the session. The plant edits below are byte-identical to those applied on
# 2026-09-02 (pass 1, P1-P6); results in matrix-run.log. TGT = the pinned clone (1eac312d).
import subprocess, time, os
TGT="<WORKDIR>/verify-005-target"; POETRY=os.path.expanduser("~/.venv-poetry/bin/poetry"); os.chdir(TGT)
PLANTS=[
 ("P1","T2","src/grpc/client.py",'if ack.HasField("committed_cursor") and not success:','if ack.HasField("committed_cursor") and False:',"failed batch WITH cursor now advances checkpoint"),
 ("P2","T3","src/state/dead_letter_queue.py",'                    return False','                    return True',"permanently-lost DLQ record reported as stored"),
 ("P3","T4*","src/engine/mapping.py",'return pc.cast(column, field.type, safe=True)','return pc.cast(column, field.type, safe=False)',"lossy narrowing silently truncates [HINT-EXPOSED]"),
 ("P4","T4*","src/state/store.py",'return {_TYPE_KEY: "datetime", _VALUE_KEY: value.isoformat()}','return {_TYPE_KEY: "datetime", _VALUE_KEY: value.replace(tzinfo=None).isoformat()}',"cursor datetime loses tz [HINT-EXPOSED]"),
 ("P5","T1*","src/grpc/cursor.py",'elif _compare_values(cursor_value, max_cursor_value) > 0:','elif _compare_values(cursor_value, max_cursor_value) >= 0:',"equal cursor bypasses tie-breaker [HINT-EXPOSED]"),
 ("P6","T3","src/state/dead_letter_queue.py",'        if written:','        if True:',"phantom DLQ count on failed write"),
]
def run_suite():
    t=time.time(); r=subprocess.run([POETRY,"run","pytest","-p","no:cacheprovider","-x","-q","--no-header"],capture_output=True,text=True,timeout=400)
    return r.returncode,(r.stdout+r.stderr),time.time()-t
for pid,inv,f,old,new,note in PLANTS:
    src=open(f).read(); n=src.count(old)
    if n==0: print(f"{pid} PLANT-ERROR anchor-missing :: {note}",flush=True); continue
    open(f,"w").write(src.replace(old,new,1))          # first occurrence (P3/P6 matched twice; first = the site recorded)
    try: rc,out,dt=run_suite()
    finally: subprocess.run(["git","checkout","--",f],cwd=TGT)
    v="ESCAPED" if rc==0 else "CAUGHT" if rc==1 else f"PLANT-ERROR(rc={rc})"
    print(f"{pid} {inv:4} {v:8} {dt:5.0f}s matches={n} :: {note}",flush=True)
