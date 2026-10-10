import hashlib
import importlib.util
import tempfile
import subprocess
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("vp",ROOT/"docs/plan-check/verify_pointer.py")
vp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vp)
COMMIT = "a" * 40

class PointerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pointer = Path(self.tmp.name)/"pointer.md"
        self.fields = dict(master_repo="JimHardy-hdce/plan-check",master_path="docs/plan-check/PLAN_CHECK.md",master_ref="main",master_version="1.0.0",pinned_commit=COMMIT,sha256=vp.master_sha256(vp.DEFAULT_MASTER))
    def check(self,extra=""):
        self.pointer.write_text("".join(f"- {k}: {v}\n" for k,v in self.fields.items())+extra)
        return vp.check(self.pointer,commit=COMMIT)
    def test_match(self):
        self.assertEqual(self.check(),[])
    def test_every_field_drift(self):
        for key in self.fields:
            with self.subTest(key=key):
                saved = self.fields[key]
                self.fields[key] = "incorrect"
                self.assertTrue(any("DRIFT" in p for p in self.check()))
                self.fields[key] = saved
    def test_missing(self):
        del self.fields["master_version"]
        self.assertTrue(any("missing" in p for p in self.check()))
    def test_duplicate(self):
        self.assertTrue(any("duplicate" in p for p in self.check("- master_ref: main\n")))
    def test_body_copy(self):
        self.assertTrue(any("competing" in p for p in self.check("Build, verify, correct, continue")))
    def test_unreadable(self):
        self.assertTrue(vp.check(self.pointer,commit=COMMIT)[0].startswith("BLOCKED"))
    def test_unverifiable_commit(self):
        self.check()
        self.assertTrue(any("BLOCKED" in p for p in vp.check(self.pointer,commit="short")))
    def test_real_git_ref_and_dirty_master(self):
        root=Path(self.tmp.name)/"repo"
        root.mkdir()
        master=root/"docs/plan-check/PLAN_CHECK.md"
        master.parent.mkdir(parents=True)
        master.write_bytes(vp.DEFAULT_MASTER.read_bytes())
        def git(*args):
            return subprocess.check_output(["git","-C",str(root),*args],stderr=subprocess.DEVNULL,text=True).strip()
        git("init","-b","main")
        git("add",".")
        git("-c","user.name=Test","-c","user.email=test@example.invalid","commit","-m","fixture")
        self.fields["pinned_commit"]=git("rev-parse","HEAD")
        self.check()
        self.assertEqual(vp.check(self.pointer,master),[])
        master.write_text(master.read_text()+"\nChanged rules\n")
        self.assertTrue(any("working master" in p for p in vp.check(self.pointer,master)))
        self.assertTrue(any("BLOCKED" in p for p in vp.check(self.pointer,master,ref="absent")))
    def test_required_rule(self):
        self.assertIn("Build, verify, correct, continue, and bring you the completed result.",vp.DEFAULT_MASTER.read_text())

if __name__ == "__main__":
    unittest.main()
