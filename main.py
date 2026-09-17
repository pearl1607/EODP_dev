# Use this main so that the relative paths can be resolved
import l1b.mainL1b as l1b_main
import l1b.test.l1b_test as l1b_test

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r"C:\Users\alisa\Documents\uc3m\eodp\EODP_dev\auxiliary"
indir = r"C:\Users\alisa\Documents\uc3m\eodp\EODP_TER_2021\EODP-TS-L1B\input"
outdir = r"C:\Users\alisa\Documents\uc3m\eodp\EODP_dev\output_equal"
outdir_target = r"C:\Users\alisa\Documents\uc3m\eodp\EODP_TER_2021\EODP-TS-L1B\output"

# Run L1B
l1b_main.main(auxdir, indir, outdir)

# Run test to compare with target outputs
l1b_test.compare_netcdf_files(outdir, outdir_target,)
