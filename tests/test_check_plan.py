import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("cp",ROOT/"docs/plan-check/check_plan.py")
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

class GateTests(unittest.TestCase):
    def setUp(self):
        self.record=json.loads((ROOT/"examples/ready.json").read_text())
        self.root=ROOT/"examples/project"
    def status(self,phase="final"):
        return cp.assess(self.record,self.root,phase)["status"]
    def test_pass_both_phases(self):
        self.assertEqual(self.status("prebuild"),"PASS")
        self.assertEqual(self.status(),"PASS")
    def test_prebuild_not_completion(self):
        self.record["tasks"]["items"][0]["status"]="pending"
        self.record["evidence"]=[]
        self.assertEqual(self.status("prebuild"),"PASS")
        self.assertEqual(self.status(),"REVISE")
    def test_blockers(self):
        self.record["blockers"]=["credentials missing"]
        self.assertEqual(self.status(),"BLOCKED")
    def test_authority(self):
        self.record["authority"]["build"]=False
        self.assertEqual(self.status(),"BLOCKED")
    def test_revision_drift(self):
        for field in ("spec","plan","tasks"):
            with self.subTest(field=field):
                self.record[field]["revision"]="old"
                self.assertEqual(self.status(),"REVISE")
                self.record[field]["revision"]="example-v1"
    def test_unknown_task(self):
        self.record["plan"]["items"][0]["task_ids"]=["unknown"]
        self.assertEqual(self.status(),"REVISE")
    def test_orphan_task(self):
        task=copy.deepcopy(self.record["tasks"]["items"][0]); task["id"]="T2"
        self.record["tasks"]["items"].append(task)
        self.assertEqual(self.status(),"REVISE")
    def test_duplicate_requirement(self):
        self.record["spec"]["items"]*=2
        self.assertEqual(self.status(),"REVISE")
    def test_implementation_mapping(self):
        self.record["plan"]["items"][0]["implementation"]=["other.py"]
        self.assertEqual(self.status("prebuild"),"REVISE")
    def test_missing_implementation(self):
        self.root=Path(tempfile.gettempdir())/"nonexistent-plancheck-root"
        self.assertEqual(self.status(),"REVISE")
    def test_evidence_failures(self):
        for field,value in (("revision","old"),("result","FAIL"),("sha256","0"*64),("requirement_id","unknown"),("path","missing.txt")):
            with self.subTest(field=field):
                item=self.record["evidence"][0];saved=item[field];item[field]=value
                self.assertEqual(self.status(),"REVISE");item[field]=saved
    def test_implementation_changed_since_evidence(self):
        self.record["evidence"][0]["implementation_sha256"]["hello.py"]="0"*64
        self.assertEqual(self.status(),"REVISE")
    def test_evidence_implementation_coverage(self):
        self.record["evidence"][0]["implementation_sha256"]={}
        self.assertEqual(self.status(),"REVISE")
    def test_path_escape(self):
        for path in ("../secret","/etc/passwd","C:/secret","folder\\secret"):
            with self.subTest(path=path):
                self.record["evidence"][0]["path"]=path
                self.assertEqual(self.status(),"REVISE")
    def test_malformed_records(self):
        for record in (None,[],{}, {"schema_version":1,"revision":[]}):
            self.assertEqual(cp.assess(record,self.root)["status"],"REVISE")
    def test_malformed_schema_version(self):
        self.record["schema_version"] = True
        self.assertEqual(self.status(), "REVISE")
    def test_malformed_collections(self):
        original = copy.deepcopy(self.record)
        for section, field in (("plan", "task_ids"), ("plan", "implementation"), ("tasks", "implementation")):
            with self.subTest(section=section, field=field):
                self.record = copy.deepcopy(original)
                self.record[section]["items"][0][field] = "hello.py"
                self.assertEqual(self.status(), "REVISE")
    def test_invalid_blocker_collection(self):
        self.record["blockers"] = ""
        self.assertEqual(self.status(), "REVISE")
    def test_invalid_phase(self):
        self.assertEqual(self.status("invalid"),"REVISE")
    def test_correction_converges(self):
        original=copy.deepcopy(self.record)
        self.record["evidence"][0]["result"]="FAIL"
        self.assertEqual(self.status(),"REVISE")
        self.record=original
        self.assertEqual(self.status(),"PASS")

if __name__ == "__main__":
    unittest.main()
