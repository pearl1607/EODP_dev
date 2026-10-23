
# LEVEL-1B MODULE

from l1b.src.initL1b import initL1b
from common.io.writeToa import writeToa, readToa
from common.src.auxFunc import getIndexBand
from common.io.readFactor import readFactor, EQ_MULT, EQ_ADD, NC_EXT
import numpy as np
import os
import matplotlib.pyplot as plt

class l1b(initL1b):

    def __init__(self, auxdir, indir, outdir):
        super().__init__(auxdir, indir, outdir)

    def processModule(self):

        self.logger.info("Start of the L1B Processing Module")

        for band in self.globalConfig.bands:

            self.logger.info("Start of BAND " + band)

            # Read TOA - output of the ISM in Digital Numbers
            # -------------------------------------------------------------------------------
            toa = readToa(self.indir, self.globalConfig.ism_toa + band + '.nc')

            # Store original raw DN for plotting
            toa_raw = toa.copy()
            toa_eq = None
            eq_mult = None
            eq_add = None

            # Equalization (radiometric correction)
            # -------------------------------------------------------------------------------
            if self.l1bConfig.do_equalization:
                self.logger.info("EODP-ALG-L1B-1010: Radiometric Correction (equalization)")

                # Read the multiplicative and additive factors from auxiliary/equalization/
                eq_mult = readFactor(os.path.join(self.auxdir,self.l1bConfig.eq_mult+band+NC_EXT),EQ_MULT)
                eq_add = readFactor(os.path.join(self.auxdir,self.l1bConfig.eq_add+band+NC_EXT),EQ_ADD)

                # Do the equalization and save to file
                toa = self.equalization(toa, eq_add, eq_mult)
                toa_eq = toa.copy()
                writeToa(self.outdir, self.globalConfig.l1b_toa_eq + band, toa)

            # Restitution (absolute radiometric gain)
            # -------------------------------------------------------------------------------
            self.logger.info("EODP-ALG-L1B-1020: Absolute radiometric gain application (restoration)")
            toa = self.restoration(toa, self.l1bConfig.gain[getIndexBand(band)])

            # Write output TOA
            # -------------------------------------------------------------------------------
            writeToa(self.outdir, self.globalConfig.l1b_toa + band, toa)
            self.plotL1bToa(toa, self.outdir, band)

            self.plotCalibration(
                toa_raw=toa_raw,
                toa_eq=toa_eq,
                toa_l1b=toa,
                eq_add=eq_add,
                eq_mult=eq_mult,
                gain=self.l1bConfig.gain[getIndexBand(band)],
                outputdir=self.outdir,
                band=band
            )

            self.logger.info("End of BAND " + band)

        self.logger.info("End of the L1B Module!")

    def equalization(self, toa, eq_add, eq_mult):
        """
        Equlization. Apply an offset and a gain.
        :param toa: TOA in DN
        :param eq_add: Offset in DN
        :param eq_mult: Gain factor, adimensional
        :return: TOA in DN, equalized
        """
        toa = (toa - eq_add) / eq_mult
        return toa

    def restoration(self, toa, gain):
        """
        Absolute Radiometric Gain - restore back to radiances
        :param toa: TOA in DN
        :param gain: gain in [rad/DN]
        :return: TOA in radiances [mW/sr/m2]
        """
        toa = toa * gain
        self.logger.debug('Sanity check. TOA in radiances after gain application ' + str(toa[1, -1]) + ' [mW/m2/sr]')

        return toa

    def plotL1bToa(self, toa_l1b, outputdir, band):
        """
        Plot the L1B TOA after radiometric correction and restoration.

        :param toa_l1b: L1B TOA image in radiances [mW/sr/m2]
        :param outputdir: Output directory
        :param band: Spectral band
        """
        # TOA in 2D image
        plt.figure()
        plt.imshow(toa_l1b, aspect='auto')
        plt.colorbar(label='Radiance [mW/sr/m²]')
        plt.title('L1B TOA - Band ' + band)
        plt.xlabel('ACT')
        plt.ylabel('ALT')

        filename_2d = os.path.join(
            outputdir,
            'l1b_toa_' + band + '_2D.png'
        )

        plt.savefig(filename_2d, dpi=300, bbox_inches='tight')
        plt.close()

        # TOA cut for the central ALT position
        idalt = toa_l1b.shape[0] // 2
        plt.figure()
        plt.plot(toa_l1b[idalt, :])
        plt.title(
            'L1B TOA - Band ' + band +
            ' - ALT ' + str(idalt)
        )
        plt.xlabel('ACT')
        plt.ylabel('Radiance [mW/sr/m²]')
        plt.grid(True)
        filename_1d = os.path.join(
            outputdir,
            'l1b_toa_' + band + '_ALT' + str(idalt) + '.png'
        )
        plt.savefig(filename_1d, dpi=300, bbox_inches='tight')
        plt.close()

    def plotCalibration(self, toa_raw, toa_eq, toa_l1b, eq_add, eq_mult, gain, outputdir, band):
        """
        Plot L1B calibration steps:
        raw DN -> equalized DN -> radiance.

        :param toa_raw: raw ISM TOA in DN
        :param toa_eq: equalized TOA in DN
        :param toa_l1b: restored L1B TOA in radiance
        :param eq_add: additive equalization factor
        :param eq_mult: multiplicative equalization factor
        :param gain: absolute radiometric gain
        :param outputdir: output directory
        :param band: band name
        """

        idalt = toa_raw.shape[0] // 2

        # -------------------------------------------------------------------------
        # Plot central row: raw DN, equalized DN, final radiance
        # -------------------------------------------------------------------------
        fig, ax1 = plt.subplots(figsize=(10, 5))

        ax1.plot(toa_raw[idalt, :], label='Raw ISM DN', color='tab:blue', linewidth=1)
        if toa_eq is not None:
            ax1.plot(toa_eq[idalt, :], label='Equalized DN', color='tab:orange', linewidth=1)

        ax1.set_xlabel('ACT pixel')
        ax1.set_ylabel('Digital Number [DN]')
        ax1.grid(True)

        ax2 = ax1.twinx()
        ax2.plot(toa_l1b[idalt, :], label='L1B radiance', color='tab:green', linestyle="dotted", linewidth=1)
        ax2.set_ylabel('Radiance [mW/m²/sr]')

        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='best')

        plt.title('L1B calibration profile - Band ' + band + ' - ALT ' + str(idalt))

        filename = os.path.join(outputdir, 'l1b_calibration_profile_' + band + '.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        # -------------------------------------------------------------------------
        # Histogram before and after calibration
        # -------------------------------------------------------------------------
        plt.figure(figsize=(8, 5))

        plt.hist(toa_raw.flatten(), bins=100, alpha=0.5, label='Raw ISM DN')

        if toa_eq is not None:
            plt.hist(toa_eq.flatten(), bins=100, alpha=0.5, label='Equalized DN')

        plt.xlabel('Digital Number [DN]')
        plt.ylabel('Number of pixels')
        plt.title('L1B calibration histogram - Band ' + band)
        plt.legend()
        plt.grid(True)

        filename = os.path.join(outputdir, 'l1b_calibration_histogram_' + band + '.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
