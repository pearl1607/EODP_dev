# Use this main so that the relative paths can be resolved
import l1b.mainL1b as l1b_main
import l1b.test.l1b_test as l1b_test
import ism.mainIsm as ism_main

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r"C:\Users\alisa\Documents\uc3m\eodp\EODP_dev\auxiliary"
indir = r"C:\Users\alisa\Documents\uc3m\eodp\EODP_TER_2021\EODP-TS-L1B\input"
outdir = r"C:\Users\alisa\Documents\uc3m\eodp\EODP_dev\output_equal"
outdir_target = r"C:\Users\alisa\Documents\uc3m\eodp\EODP_TER_2021\EODP-TS-L1B\output"

indir_ism = r"C:\Users\alisa\Documents\uc3m\eodp\EODP_TER_2021\EODP-TS-ISM\input\gradient_alt100_act150" # small scene
outdir_ism = r"C:\Users\alisa\Documents\uc3m\eodp\EODP_dev\ism_my_output"
outdir_ism_target = r"C:\Users\alisa\Documents\uc3m\eodp\EODP_TER_2021\EODP-TS-ISM\output"

# Run L1B
l1b_main.main(auxdir, indir, outdir)

# Run test to compare with target outputs
l1b_test.compare_netcdf_files(outdir, outdir_target, "l1b_toa_VNIR-")

# Run ISM
ism_main.main(auxdir, indir_ism, outdir_ism)

# Test ism outputs
l1b_test.compare_netcdf_files(outdir_ism, outdir_ism_target, "ism_toa_isrf_VNIR-")
