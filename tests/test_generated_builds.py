"""Build bundled Python templates without network and import their installed wheel in isolation."""
import subprocess
import sys
from pathlib import Path
import zipfile
import pytest
from blackforge.core.generator import generate_project
from blackforge.core.templates import list_templates

TEMPLATES=[name for name in list_templates() if name != "obeos-skill"]

@pytest.mark.parametrize("template",TEMPLATES)
def test_generated_template_build_and_isolated_import(template,tmp_path):
    project=generate_project(template,"sample-tool",tmp_path).destination
    if not (project/"pyproject.toml").exists():
        pytest.skip("Documentation-only template")
    output=tmp_path/"wheels"
    result=subprocess.run([sys.executable,"-I","-m","build","--wheel","--no-isolation","--outdir",str(output),str(project)],
                          capture_output=True,text=True,timeout=60)
    assert result.returncode==0,result.stdout+result.stderr
    wheel=next(output.glob("*.whl"))
    installed=tmp_path/"installed"
    with zipfile.ZipFile(wheel) as archive:archive.extractall(installed)
    modules=[p.name for p in installed.iterdir() if p.is_dir() and (p/"__init__.py").exists()]
    assert modules,"Generated wheel contains no Python package"
    check=subprocess.run([sys.executable,"-I","-c",
        "import importlib,sys;sys.path.insert(0,sys.argv[1]);[importlib.import_module(name) for name in sys.argv[2:]]",
        str(installed),*modules],cwd=tmp_path,capture_output=True,text=True,timeout=15)
    assert check.returncode==0,check.stdout+check.stderr
