result = (2000 - 1970) * 365 * 24 * 3600 + (
            mon_yday[isleap((*dt).tm_year)][(*dt).tm_mon - 1] + (*dt).tm_mday - 1) * 24 * 3600 + 0 * 3600 + 0 * 60 + 0;
