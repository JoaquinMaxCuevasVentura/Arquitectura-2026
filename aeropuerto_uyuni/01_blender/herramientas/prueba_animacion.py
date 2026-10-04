"""48 cuadros a 1080p con/sin OIDN. Coste de prueba: 32 muestras, ruido .03.

blender -b uyuni_v2.blend -P herramientas/prueba_animacion.py -- --out DIR
El perfil de producción del archivo y de render_plan no se modifica en disco.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from herramientas import render_plan

if __name__=="__main__":
    argv=sys.argv[sys.argv.index("--")+1:]
    render_plan.PROFILES["drone"]=dict(samples=32,threshold=.03,clamp=8.0,percent=100)
    render_plan.main(["--mode","drone-test","--profile","final","--revision","test_1080p_32m",
                      "--compositor","optics","--transparent-bounces","16","--encode",*argv])
