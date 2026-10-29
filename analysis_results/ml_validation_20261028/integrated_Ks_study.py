"""Same predeclared method family for the pilot's successful integrated Ks target."""
from pathlib import Path
import model_study as m
O=Path(__file__).resolve().parent/'integrated_Ks';O.mkdir(exist_ok=True);(O/'models').mkdir(exist_ok=True)
m.O=O;m.TARGETS=['A_Ks'];m.run()
