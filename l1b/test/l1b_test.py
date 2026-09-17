
from pathlib import Path
import numpy as np
from netCDF4 import Dataset

RTOL = 1e-5
ATOL = 1e-8


def compare_netcdf_files(output_folder, target_folder, filename,
                         rtol=RTOL, atol=ATOL):

    output_folder = Path(output_folder)
    target_folder = Path(target_folder)

    output_files = sorted(
        output_folder.glob(filename + "*.nc")
    )

    if not output_files:
        print(f"No matching NetCDF files found for {filename}.")
        return False

    all_files_equal = True

    for output_file in output_files:

        target_file = target_folder / output_file.name

        print(f"\nComparing: {output_file.name}")

        if not target_file.exists():
            print("  ERROR: Target file does not exist.")
            all_files_equal = False
            continue

        file_equal = True

        try:
            with Dataset(output_file, "r") as output_ds, \
                 Dataset(target_file, "r") as target_ds:

                # Check dimensions
                output_dims = {
                    name: len(dim)
                    for name, dim in output_ds.dimensions.items()
                }

                target_dims = {
                    name: len(dim)
                    for name, dim in target_ds.dimensions.items()
                }

                if output_dims != target_dims:
                    print("  ERROR: Dimensions differ.")
                    print(f"  Output: {output_dims}")
                    print(f"  Target: {target_dims}")
                    all_files_equal = False
                    continue

                # Check variables
                if set(output_ds.variables) != set(target_ds.variables):
                    print("  ERROR: Variable names differ.")
                    print("  Output:", set(output_ds.variables))
                    print("  Target:", set(target_ds.variables))
                    all_files_equal = False
                    continue

                for variable_name in output_ds.variables:

                    output_var = output_ds.variables[variable_name]
                    target_var = target_ds.variables[variable_name]

                    output_data = output_var[:]
                    target_data = target_var[:]

                    # Check shape
                    if output_data.shape != target_data.shape:
                        print(
                            f"  DIFFERENT: {variable_name} "
                            f"(shape mismatch)"
                        )
                        file_equal = False
                        continue

                    # Numerical comparison
                    equal = np.allclose(
                        output_data,
                        target_data,
                        rtol=rtol,
                        atol=atol,
                        equal_nan=True
                    )

                    if equal:
                        print(f"  OK: {variable_name}")
                    else:
                        difference = np.abs(
                            output_data - target_data
                        )

                        max_difference = np.nanmax(difference)

                        print(
                            f"  DIFFERENT: {variable_name} "
                            f"(max difference: "
                            f"{max_difference:.6e})"
                        )

                        file_equal = False

                if file_equal:
                    print("  => FILE IDENTICAL WITHIN TOLERANCE")
                else:
                    print("  => FILES DIFFER")

                all_files_equal = all_files_equal and file_equal

        except Exception as error:
            print(f"  ERROR while reading files: {error}")
            all_files_equal = False

    print("\n" + "=" * 50)

    if all_files_equal:
        print("ALL FILES ARE IDENTICAL WITHIN TOLERANCE.")
    else:
        print("SOME FILES DIFFER.")

    return all_files_equal
