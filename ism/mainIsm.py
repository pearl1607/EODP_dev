
# MAIN FUNCTION TO CALL THE ISM MODULE

from ism.src.ism import ism


def main(auxdir: str, indir: str, outdir: str):
    # Initialise the ISM
    myIsm = ism(auxdir, indir, outdir)
    myIsm.processModule()
