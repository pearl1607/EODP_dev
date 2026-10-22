# Use this main so that the relative paths can be resolved
import l1b.mainL1b as l1b_main
import l1b.test.l1b_test as l1b_test
import ism.mainIsm as ism_main
import l1c.mainL1c as l1c_main

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r"C:\Users\alisa\Documents\uc3m\eodp\EODP_dev\auxiliary"

ism_test_input = r"C:\Users\alisa\Documents\uc3m\eodp\EODP-TS-E2E\sgm_out"

outdir_ism = r"C:\Users\alisa\Documents\uc3m\eodp\output_e2e_ism"
outdir_l1b = r"C:\Users\alisa\Documents\uc3m\eodp\output_e2e_l1b"
input_l1c = r"C:\Users\alisa\Documents\uc3m\eodp\EODP-TS-E2E\gm_out,C:\Users\alisa\Documents\uc3m\eodp\output_e2e_l1b"
outdir_l1c = r"C:\Users\alisa\Documents\uc3m\eodp\output_e2e_l1c"

outdir_ism_target = r"C:\Users\alisa\Documents\uc3m\eodp\EODP_TER_2021\EODP-TS-ISM\output"
outdir_l1b_target = r"C:\Users\alisa\Documents\uc3m\eodp\EODP_TER_2021\EODP-TS-L1B\output"
outdir_l1c_target = r"C:\Users\alisa\Documents\uc3m\eodp\EODP_TER_2021\EODP-TS-L1C\output"

# Run ISM
ism_main.main(auxdir, ism_test_input, outdir_ism)

# Test ism outputs
l1b_test.compare_netcdf_files(outdir_ism, outdir_ism_target, "ism_toa_isrf_VNIR-")

# Run L1B
l1b_main.main(auxdir, outdir_ism, outdir_l1b)

# Test l1b outputs
l1b_test.compare_netcdf_files(outdir_l1b, outdir_l1b_target, "l1b_toa_VNIR-")

# Run L1C
l1c_main.main(auxdir, input_l1c, outdir_l1c)

# Test l1c outputs
l1b_test.compare_netcdf_files(outdir_l1c, outdir_l1c_target, "l1c_toa_VNIR-")
