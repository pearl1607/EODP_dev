
# LEVEL-1C

from l1c.src.initL1c import initL1c
from common.io.writeToa import writeToa, readToa
from common.io.readGeodetic import readGeodetic, getCorners
import mgrs
import numpy as np
from scipy.interpolate import bisplrep, bisplev
import matplotlib.pyplot as plt
from common.io.l1cProduct import writeL1c
from matplotlib import cm
import os
from common.src.auxGeom import haversine


class l1c(initL1c):

    def __init__(self, auxdir, indir, outdir):
        super().__init__(auxdir, indir, outdir)

    def processModule(self):

        self.logger.info("Start of the L1C Processing Module")

        for band in self.globalConfig.bands:

            self.logger.info("Start of BAND " + band)

            # Read TOA - output of the L1B in Radiances
            # -------------------------------------------------------------------------------
            toa = readToa(self.l1bdir, self.globalConfig.l1b_toa + band + '.nc')
            lat, lon = readGeodetic(self.gmdir, self.globalConfig.gm_geoloc)
            self.checkSize(lat, toa)

            # L1C reprojection onto the MGRS grid
            # -------------------------------------------------------------------------------
            lat_l1c, lon_l1c, toa_l1c = self.l1cProjtoa(lat, lon, toa, band)

            # Write output TOA
            # -------------------------------------------------------------------------------
            writeL1c(self.outdir, self.globalConfig.l1c_toa + band, lat_l1c, lon_l1c, toa_l1c)

            self.logger.info("End of BAND " + band)

        self.logger.info("End of the L1C Module!")

    def l1cProjtoa(self, lat, lon, toa, band):
        '''
        This function reprojects the L1B radiances into the MGRS grid.

        The MGRS reference system
        https://www.bluemarblegeo.com/knowledgebase/calculator-2020/Military_Grid_Reference_System_(MGRS).htm
        MGRS: '31REQ4367374067'
        31 is the UTM zone, R is the UTM latitude band; EQ are the MGRS column and row band letters
        43673 is the MGRS Easting (5 dig); 74067 is the MGRS Northing (5dig)

        Python mgrs library documentation
        https://pypi.org/project/mgrs/

        :param lat: L1B latitudes [deg]
        :param lon: L1B longitudes [deg]
        :param toa: L1B radiances
        :param band: band
        :return: L1C radiances, L1C latitude and longitude in degrees
        '''
        tck = bisplrep(lat, lon, toa)
        m = mgrs.MGRS()
        mgrs_tiles = set([])

        for ii in range(toa.shape[0]):
            for jj in range(toa.shape[1]):
                mgrs_tiles.add(str(m.toMGRS(lat[ii, jj], lon[ii, jj], MGRSPrecision=self.l1cConfig.mgrs_tile_precision)))

        mgrs_tiles = list(mgrs_tiles)
        len_mgrs = len(mgrs_tiles)
        toa_l1c = np.zeros(len_mgrs)
        lat_l1c = np.zeros(len_mgrs)
        lon_l1c = np.zeros(len_mgrs)

        for ii in range(len_mgrs):
            lattt, lonnn = m.toLatLon(mgrs_tiles[ii])
            lat_l1c[ii] = lattt
            lon_l1c[ii] = lonnn
            toa_l1c[ii] = bisplev(lattt, lonnn, tck)

        # Make plots
        self.plot_l1b_vs_l1c(lat, lon, lat_l1c, lon_l1c, band)
        self.plot_spatial_sampling_distance(lat, lon, band)

        return lat_l1c, lon_l1c, toa_l1c

    def plot_l1b_vs_l1c(self, lat_l1b, lon_l1b, lat_l1c, lon_l1c, band):
        """
        Plot L1B and L1C geographic grids.

        L1B grid is shown in red.
        L1C grid is shown in blue.
        """
        plt.figure()

        # Not plot all lines to increase readability and runtime
        step = 1000

        # L1B grid
        # Plot outer boundary of L1B grid
        plt.plot(lon_l1b[0, :], lat_l1b[0, :], 'b-', linewidth=0.8, label='L1B grid boundary')
        plt.plot(lon_l1b[-1, :], lat_l1b[-1, :], 'b-', linewidth=0.8)
        plt.plot(lon_l1b[:, 0], lat_l1b[:, 0], 'b-', linewidth=0.8)
        plt.plot(lon_l1b[:, -1], lat_l1b[:, -1], 'b-', linewidth=0.8)

        # L1C grid
        plt.scatter(lon_l1c, lat_l1c, s=0.2, c="red", label='L1C MGRS grid')

        plt.xlabel('Longitude [deg]')
        plt.ylabel('Latitude [deg]')
        plt.title('L1B and L1C geographic grids')
        plt.legend()
        plt.grid(True)
        plt.axis('equal')

        filename = os.path.join(self.outdir, "l1b_l1c_grid_" + band + ".png")

        plt.savefig(filename, dpi=150)
        plt.close()

    def plot_spatial_sampling_distance(self, lat_l1b, lon_l1b, band):
        """
        Plot the spatial sampling distance between adjacent L1B pixels along the central row.
        """
        n_alt = lat_l1b.shape[0]
        n_act = lat_l1b.shape[1]

        central_row = n_alt // 2
        central_col = n_act // 2

        # -------------------------------------------------------------------------
        # ACT GSD along the central ALT row
        # -------------------------------------------------------------------------
        gsd_act = np.zeros(n_act - 1)

        for j in range(n_act - 1):
            gsd_act[j] = haversine(
                lat_l1b[central_row, j],
                lon_l1b[central_row, j],
                lat_l1b[central_row, j + 1],
                lon_l1b[central_row, j + 1]
            )

        act_pixels = np.arange(n_act - 1)

        # -------------------------------------------------------------------------
        # ALT GSD along the central ACT column
        # -------------------------------------------------------------------------
        gsd_alt = np.zeros(n_alt - 1)

        for i in range(n_alt - 1):
            gsd_alt[i] = haversine(
                lat_l1b[i, central_col],
                lon_l1b[i, central_col],
                lat_l1b[i + 1, central_col],
                lon_l1b[i + 1, central_col]
            )

        alt_pixels = np.arange(n_alt - 1)

        # -------------------------------------------------------------------------
        # Combined line plot
        # -------------------------------------------------------------------------
        plt.figure(figsize=(10, 5))

        plt.plot(act_pixels, gsd_act, label='ACT GSD, central ALT row ' + str(central_row))
        plt.plot(alt_pixels, gsd_alt, label='ALT GSD, central ACT column ' + str(central_col))

        plt.xlabel('Pixel index')
        plt.ylabel('Ground Sampling Distance [m]')
        plt.title('L1B Ground Sampling Distance ACT/ALT - Band ' + band)
        plt.grid(True)
        plt.legend()

        filename = os.path.join(self.outdir, 'l1b_gsd_act_alt_' + band + '.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        # -------------------------------------------------------------------------
        # Separate ACT GSD plot
        # -------------------------------------------------------------------------
        plt.figure(figsize=(10, 5))
        plt.plot(act_pixels, gsd_act, color='tab:blue')
        plt.xlabel('ACT pixel')
        plt.ylabel('ACT GSD [m]')
        plt.title('ACT Ground Sampling Distance - Band ' + band)
        plt.grid(True)

        filename = os.path.join(self.outdir, 'l1b_gsd_act_' + band + '.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        # -------------------------------------------------------------------------
        # Separate ALT GSD plot
        # -------------------------------------------------------------------------
        plt.figure(figsize=(10, 5))
        plt.plot(alt_pixels, gsd_alt, color='tab:orange')
        plt.xlabel('ALT pixel')
        plt.ylabel('ALT GSD [m]')
        plt.title('ALT Ground Sampling Distance - Band ' + band)
        plt.grid(True)

        filename = os.path.join(self.outdir, 'l1b_gsd_alt_' + band + '.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        # -------------------------------------------------------------------------
        # Print useful statistics to logger
        # -------------------------------------------------------------------------
        self.logger.info(
            'ACT GSD Band ' + band +
            ': mean=' + str(np.nanmean(gsd_act)) +
            ' m, min=' + str(np.nanmin(gsd_act)) +
            ' m, max=' + str(np.nanmax(gsd_act)) + ' m'
        )

        self.logger.info(
            'ALT GSD Band ' + band +
            ': mean=' + str(np.nanmean(gsd_alt)) +
            ' m, min=' + str(np.nanmin(gsd_alt)) +
            ' m, max=' + str(np.nanmax(gsd_alt)) + ' m'
        )

    def checkSize(self, lat, toa):
        '''
        Check the sizes of the input radiances and geodetic coordinates.
        If they don't match, exit.
        :param lat: Latitude 2D matrix
        :param toa: Radiance 2D matrix
        :return: NA
        '''
        assert (np.shape(lat) == np.shape(toa))
