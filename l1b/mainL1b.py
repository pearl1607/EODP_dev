
# MAIN FUNCTION TO CALL THE L1B MODULE

from l1b.src.l1b import l1b


def main(auxdir: str, indir: str, outdir: str):
    # Initialise the ISM
    myL1b = l1b(auxdir, indir, outdir)
    myL1b.processModule()
