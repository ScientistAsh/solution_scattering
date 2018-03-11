### use python 3 error & statement
import datetime
import math

now = datetime.datetime.now()
release = datetime.datetime(2008, 12, 3)
deltaT = now-release
years  = math.floor((deltaT.days) / 365)
days = deltaT.days - years*365

import sys
if sys.version_info[0] < 3:
    print("\nException: Please use Python 3, it has been out for {} years {} days, and 2.7 may soon be unsupported (http://www.python3statement.org/)".format(years,days))
    sys.exit(1)

### import needed modules & functions
from time import clock
import parse
import pathlib
from scipy.stats import chisquare
import scipy.integrate as integrate
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
plt.style.use('ggplot')
from collections import OrderedDict
import numpy as np
from numpy.linalg import svd
from trace import Trace
from new_analysis import real_space_plotter
import pickle


# script, directory = sys.argv
# reference = parse.parse("/Volumes/beryllium/saxs_waxs_tjump/Trypsin/Trypsin-BA-Buffer-1/xray_images/Trypsin-BA-Buffer-1_26_-10us-10.tpkl")
# reference = parse.parse("/Volumes/beryllium/saxs_waxs_tjump/cypa/APS_20170302/CypA-WT-1/xray_images/CypA-WT-1_9_4.22us.tpkl")
# reference = parse.parse("/Volumes/beryllium/saxs_waxs_tjump/cypa/APS_20160701/CypA-S99T/CypA-S99T-1/xray_images/CypA-S99T-1_9_75ns_off.tpkl")
reference = parse.parse("/Volumes/LaCie/radial_averages/Lysozyme-apo/Lysozyme-apo-Buffer-1/xray_images/Lysozyme-apo-Buffer-1_2_3C_1_23.7us.tpkl")

CHI_OUTLIER = 1.5
t_shortlist = ["-10.1us", "1us", "10us", "100us", "1ms"]
# t_shortlist = ["562ns"]
# t_shortlist = ["-10.1us", "562ns", "750ns", "1us", "1.33us", "1.78us", "2.37us", "3.16us", "4.22us", "5.62us"]
TIMES = [ "562ns", "750ns", "1us", "1.33us", "1.78us", "2.37us", "3.16us", "4.22us", "5.62us", "7.5us", "10us", "13.3us", "17.8us", "23.7us", "31.6us", "42.2us", "56.2us", "75us", "100us", "133us", "178us", "237us", "316us", "422us", "562us"]



def sample_map_multitemp(samp_dir, multitemp=None):
    samp_dir = pathlib.Path(samp_dir)
    samp_files = list(samp_dir.glob(pattern='**/*.tpkl'))
    # buffer_files = list(buff.glob(pattern='**/*.tpkl'))
    t0 = clock()
    REPS = []
    TIMES = []
    ITERATIONS = []
    TEMPS = []
    for file in samp_files:
        name = file.name
        parent = file.parent
        if multitemp:
            samp, iteration, temp, rep, time = name.split('_')
            time = time.replace('.tpkl','')
        else:
            samp, rep, time, onoff = name.split('_')
        # time = time.replace('.tpkl','')
        REPS.append(rep)
        TIMES.append(time)
        ITERATIONS.append(iteration)
        TEMPS.append(temp)

    REPS = sorted(list(set(REPS)), key=float)
    TIMES = list(set(TIMES))
    ITERATIONS = sorted(list(set(ITERATIONS)), key=float)
    TEMPS = list(set(TEMPS))
    OFFS = [item for item in TIMES if "-10us" in item]
    ONS = [item for item in TIMES if "-10us" not in item]
    # OFFS = [item for item in TIMES if "off" in item]
    # ONS = [item for item in TIMES if "on" not in item]

    tup =  [parse.unit_sort(item) for item in ONS]
    tup_sort = sorted(tup, key=lambda item: (item[0],parse.natural_keys(item[1])))
    clean_ons = [item[1] for item in tup_sort]
    on_off_map = {k:v for k,v in (zip(clean_ons,sorted(OFFS, key=parse.alphanum_key)))}
    # on_off_map = {k:v for k,v in (zip(clean_ons,sorted(OFFS, key=parse.alphanum_key)))}
    return parent, samp, ITERATIONS, TEMPS, REPS, on_off_map

def sample_map(samp_dir):
    samp_dir = pathlib.Path(samp_dir)
    samp_files = list(samp_dir.glob(pattern='*.tpkl'))
    # buffer_files = list(buff.glob(pattern='**/*.tpkl'))
    t0 = clock()
    REPS = []
    TIMES = []
    for file in samp_files:
        name = file.name
        parent = file.parent
        samp, rep, time = name.split('_')
        time = time.replace('.tpkl','')
        REPS.append(rep)
        TIMES.append(time)

    REPS = sorted(list(set(REPS)), key=float)
    TIMES = list(set(TIMES))
    OFFS = [item for item in TIMES if "-10us" in item]
    ONS = [item for item in TIMES if "-10us" not in item]

    tup =  [parse.unit_sort(item) for item in ONS]
    tup_sort = sorted(tup, key=lambda item: (item[0],parse.natural_keys(item[1])))
    clean_ons = [item[1] for item in tup_sort]
    on_off_map = {k:v for k,v in (zip(clean_ons,sorted(OFFS, key=parse.alphanum_key)))}

    return parent, samp, REPS, on_off_map

def static_map(samp_dir):
    samp_dir = pathlib.Path(samp_dir)
    samp_files = list(samp_dir.glob(pattern='**/*.tpkl'))
    # buffer_files = list(buff.glob(pattern='**/*.tpkl'))
    # t0 = clock()
    # sample_map = []
    REPS = []
    TEMPS = []
    SERIES = []
    # TIMES = []
    for file in samp_files:
        name = file.name
        parent = file.parent
        samp, info, rep = name.split('_')
        if "BT" in info:
            dilution = info[3:5]
            temp = info[5:]
            print(temp)
        elif "PC" in info:
            dilution = info[3:6]
            temp = info[7:]
            print(temp)
        else:
            print(info)
        rep = rep.replace(".tpkl","")
        # on_data = parse.parse(str(file))
        # on_data.alg_scale(reference)
        # sample_map.append((samp,dilution,temp,on_data))

        # time = time.replace('.tpkl','')
        REPS.append(rep)
        SERIES.append(dilution)
        TEMPS.append(temp)
        # TIMES.append(time)

    REPS = sorted(list(set(REPS)), key=float)
    TEMPS = sorted(list(set(TEMPS)), key=float)
    SERIES = sorted(list(set(SERIES)))
    # TIMES = list(set(TIMES))
    # OFFS = [item for item in TIMES if "-10us" in item]
    # ONS = [item for item in TIMES if "-10us" not in item]
    # OFFS = [item for item in TIMES if "off" in item]
    # ONS = [item for item in TIMES if "on" not in item]

    # tup =  [parse.unit_sort(item) for item in ONS]
    # tup_sort = sorted(tup, key=lambda item: (item[0],parse.natural_keys(item[1])))
    # clean_ons = [item[1] for item in tup_sort]
    # on_off_map = {k:v for k,v in (zip(clean_ons,clean_ons))}

    return parent, samp, REPS, TEMPS, SERIES

    # return sample_map

def iter_vir(samples, full_conc):
    n=0
    
    temps = set([item[2] for item in samples])
    temps = sorted(list(temps))
    concs = [full_conc/1, full_conc/3, full_conc/9]
    conc_map = {"PC0":full_conc/1, "PC1":full_conc/3, "PC2":full_conc/9 }
    q_output = []
    a2_output = []
    spf_output = []
    for temp in temps:
        sv_x = []
        sv_y = []
        I_0z = []
        for item in samples:
            if item[2] == temp:
                # x = item[3].q
                y = item[3].SA
                # data_mask = np.array(x, dtype=bool)
                # data_mask[x>0.008]=False
                # x = x[data_mask]
                # y = y[data_mask]
                # I_0 = np.exp(linregress(x,y)[1])
                # I_0z.append(I_0)
                if item[1] in conc_map.keys():
                    sv_y.append(1/y)
                    sv_x.append(conc_map[item[1]])
                else:
                    pass
                n+=1
            else:
                pass
        sv_xp = np.array(sv_x)
        # print(sv_xp.shape)
        sv_yp = np.stack(sv_y)
        # print(sv_yp.shape)
        m,b = np.polyfit(sv_xp,sv_yp,1)
        mw = 18500
        conc = 50
        # print(fit_I0)
            # fit_fxnI0 = np.poly1d(fit_I0)
            # plt.scatter(sv_xp,sv_yp, label=temp)
            # plt.plot(sv_xp,fit_fxnI0(sv_xp), label=temp+"_fit")
            # vir_stats = linregress(sv_xp,sv_yp)
            # I_0_0 = 1/vir_stats[1]
            # slope = vir_stats[0]
            # MW = 18500
            # A = slope*I_0_0/(2*MW)
            # print("\nStats for virial fit:\n{}\n".format(vir_stats))
            # print("I(0,0) = {}".format(I_0_0))
            # print("A = {}".format(A))
            # print("I(c,0) for pc0 = {}".format(I_0z[0]))
            # print("I(c,0) for pc1 = {}".format(I_0z[1]))
            # print("I(c,0) for pc2 = {}".format(I_0z[2]))
        I0q_output.append((temp,1/b))
        a2_output.append((temp,m*(1/b)/2*mw))
        spf_output.append((temp, 1/(1+m/b*conc)))

    return spf_output


def chi_stat(var, ref):
    n = len(var.q)-1.0
    chi_squared = np.sum((var.SA-ref.SA)**2/(ref.sigSA**2))/n
    return chi_squared


def chi_outliers(vectors, reference_vector):
    chi_scores = [chi_stat(i, reference_vector) for i in vectors]
    print("({}, {})".format(np.mean(chi_scores), np.std(chi_scores)))
    inliers = np.asarray(chi_scores) <= CHI_OUTLIER
    # outliers = [i for i, chi in enumerate(chi_scores) if chi>CHI_OUTLIER]
    # print("outliers= {}".format(outliers))
    return inliers

def average_traces(traces):
    one_curve = traces[0]
    mean_SA = np.mean([trace.SA for trace in traces],axis=0)
    std_err = np.std([trace.SA for trace in traces],axis=0)
    prop_err = np.sqrt(np.sum([trace.sigSA**2 for trace in traces],axis=0))/(len(traces)-1)
    tot_err = np.sqrt(std_err**2+prop_err**2)
    averaged_vector=Trace(one_curve.q, np.empty_like(one_curve.q), np.empty_like(one_curve.q), tot_err, mean_SA, np.empty_like(one_curve.q))
    return averaged_vector

def iterative_chi_filter(vectors):
    averaged_vector=average_traces(vectors)
    inliers = chi_outliers(vectors, averaged_vector)
    if False not in inliers:
        clean_vectors = vectors
    else:
        clean_vectors = [vectors[i] for i, x in enumerate(inliers) if x]
        print(len(clean_vectors))
        iterative_chi_filter(clean_vectors)
    return clean_vectors


def subtract_scaled_traces(trace_one,trace_two,buffer=None):
    err_one = (trace_one.scale_factor*trace_one.sigSA)**2
    err_two = (trace_two.scale_factor*trace_two.sigSA)**2
    err_cov = (2*trace_one.scale_factor*trace_two.scale_factor*np.cov(trace_one.sigSA,trace_two.sigSA)[0][1])
    total_err = np.sqrt(np.abs(err_one+err_two-err_cov))
    output_SA = (trace_one.scaled_SA - trace_two.scaled_SA)
    output = Trace(trace_one.q, np.empty_like(trace_one.q), np.empty_like(trace_one.q), total_err, output_SA, np.empty_like(trace_one.q))
    return output

def buffer_subtract_scaled_traces(trace_one,trace_two):
    err_one = (trace_one.buffer_scale_factor*trace_one.sigSA)**2
    err_two = (trace_two.buffer_scale_factor*trace_two.sigSA)**2
    err_cov = (2*trace_one.buffer_scale_factor*trace_two.buffer_scale_factor*np.cov(trace_one.sigSA,trace_two.sigSA)[0][1])
    total_err = np.sqrt(np.abs(err_one+err_two-err_cov))
    output_SA = (trace_one.scaled_SA - trace_two.scaled_SA)
    output = Trace(trace_one.q, np.empty_like(trace_one.q), np.empty_like(trace_one.q), total_err, output_SA, np.empty_like(trace_one.q))
    return output

def add_scaled_traces(trace_one,trace_two):
    err_one = (trace_one.scale_factor*trace_one.sigSA)**2
    err_two = (trace_two.scale_factor*trace_two.sigSA)**2
    err_cov = (2*trace_one.scale_factor*trace_two.scale_factor*np.cov(trace_one.sigSA,trace_two.sigSA)[0][1])
    total_err = np.sqrt(np.abs(err_one+err_two+err_cov))
    output_SA = (trace_one.scaled_SA + trace_two.scaled_SA)
    output = Trace(trace_one.q, np.empty_like(trace_one.q), np.empty_like(trace_one.q), total_err, output_SA, np.empty_like(trace_one.q))
    return output

def buffer_add_scaled_traces(trace_one,trace_two):
    err_one = (trace_one.buffer_scale_factor*trace_one.sigSA)**2
    err_two = (trace_two.buffer_scale_factor*trace_two.sigSA)**2
    err_cov = (2*trace_one.buffer_scale_factor*trace_two.buffer_scale_factor*np.cov(trace_one.sigSA,trace_two.sigSA)[0][1])
    total_err = np.sqrt(np.abs(err_one+err_two+err_cov))
    output_SA = (trace_one.scaled_SA + trace_two.scaled_SA)
    output = Trace(trace_one.q, np.empty_like(trace_one.q), np.empty_like(trace_one.q), total_err, output_SA, np.empty_like(trace_one.q))
    return output


def add_unscaled_traces(trace_one,trace_two):
    err_one = trace_one.sigSA**2
    err_two = trace_two.sigSA**2
    err_cov = (2*np.cov(trace_one.sigSA,trace_two.sigSA)[0][1])
    total_err = np.sqrt(np.abs(err_one+err_two+err_cov))
    output_SA = (trace_one.SA + trace_two.SA)
    output = Trace(trace_one.q, np.empty_like(trace_one.q), np.empty_like(trace_one.q), total_err, output_SA, np.empty_like(trace_one.q))
    return output

def subtract_unscaled_traces(trace_one,trace_two):
    err_one = trace_one.sigSA**2
    err_two = trace_two.sigSA**2
    err_cov = (2*np.cov(trace_one.sigSA,trace_two.sigSA)[0][1])
    total_err = np.sqrt(np.abs(err_one+err_two-err_cov))
    output_SA = (trace_one.SA - trace_two.SA)
    output = Trace(trace_one.q, np.empty_like(trace_one.q), np.empty_like(trace_one.q), total_err, output_SA, np.empty_like(trace_one.q))
    return output


def time_resolved_traces(parent, samp, reps, on_off_map, option=None, multitemp=None, iterations=None, temp=None):
    
    subtracted_vectors = {i: [] for i in on_off_map.keys()}
    
    if multitemp:
        for iteration in iterations:
            for n in reps:
                for on, off in on_off_map.items():

                    # on_string = ("{0}/{1}_{2}_{3}_on.tpkl".format(parent, samp, n, on))
                    on_string = ("{0}/{1}_{2}_{3}_{4}_{5}.tpkl".format(parent, samp, iteration, temp, n, on))
                    # if option:
                    #     on_string = ("{0}/{1}_{2}_{3}_on.tpkl".format(parent, samp, n, on))
                    # else:
                    #     on_string = ("{0}/{1}_{2}_{3}.tpkl".format(parent, samp, n, on))

                    # if multitemp:
                    #     on_string = ("{0}/{1}_{2}_{3}_{4}_{5}.tpkl".format(parent, samp, iteration, temp, n, on))
                    try:
                        on_data = parse.parse(on_string)
                        on_data.alg_scale(reference)
                    except:
                        print(on_string+"\tfailed")
                        pass

                    # off_string = ("{0}/{1}_{2}_{3}_off.tpkl".format(parent, samp, n, off))
                    off_string = ("{0}/{1}_{2}_{3}_{4}_{5}.tpkl".format(parent, samp, iteration, temp, n, off))
                    # if option:
                    #     off_string = ("{0}/{1}_{2}_{3}_on.tpkl".format(parent, samp, n, off))
                    # else:
                    #     off_string = ("{0}/{1}_{2}_{3}.tpkl".format(parent, samp, n, off))
                    
                    # if multitemp:
                    #     off_string = ("{0}/{1}_{2}_{3}_{4}_{5}.tpkl".format(parent, samp, iteration, temp, n, off))
                    
                    try:
                        off_data = parse.parse(off_string)
                        off_data.alg_scale(reference)
                    except:
                        print(off_string+"\tfailed")
                        pass

                    if isinstance(on_data,type(None)) or isinstance(off_data,type(None)):
                        print(on_string+"\tfailed")
                        pass
                    else:
                        sub_scaled = subtract_scaled_traces(on_data,off_data)
                        subtracted_vectors[on].append(sub_scaled)

    else:
        for n in reps:
            for on, off in on_off_map.items():

                if option:
                    on_string = ("{0}/{1}_{2}_{3}_on.tpkl".format(parent, samp, n, on))
                else:
                    on_string = ("{0}/{1}_{2}_{3}.tpkl".format(parent, samp, n, on))

                try:
                    on_data = parse.parse(on_string)
                    on_data.alg_scale(reference)
                except:
                    print(on_string+"\tfailed")
                    pass


                if option:
                    off_string = ("{0}/{1}_{2}_{3}_on.tpkl".format(parent, samp, n, off))
                else:
                    off_string = ("{0}/{1}_{2}_{3}.tpkl".format(parent, samp, n, off))
                
                
                try:
                    off_data = parse.parse(off_string)
                    off_data.alg_scale(reference)
                except:
                    print(off_string+"\tfailed")
                    pass

                if isinstance(on_data,type(None)) or isinstance(off_data,type(None)):
                    print(on_string+"\tfailed")
                    pass
                else:
                    sub_scaled = subtract_scaled_traces(on_data,off_data)
                    subtracted_vectors[on].append(sub_scaled)

    return subtracted_vectors


def static_traces(parent, samp, reps, temps, series, option=None):
    
    static_vectors = {i: [] for i in temps}

    for temp in temps:
        buff = []
        for n in reps:
            buff_string = ("{0}/{1}_offBT{2}_{3}.tpkl".format(parent, samp, temp, n))
            try:
                buff_data = parse.parse(buff_string)
                buff_data.alg_scale(reference, overwrite=True)
                buff.append(buff_data)
            except:
                print(buff_string+"\tfailed")
                pass
        try:
            buff_filtered = iterative_chi_filter(buff)
            buff_filt_avg = average_traces(buffer_filtered)
        except:
            print("temp {}C failed for buffer".format(temp))

        for dilution in series:
            if dilution == "BT":
                pass
            else:
                stat = []
                for n in reps:
                    static_string = ("{0}/{1}_off{2}{3}_{4}.tpkl".format(parent, samp, dilution, temp, n))

                    try:
                        static_data = parse.parse(static_string)
                        static_data.alg_scale(reference, overwrite=True)
                        static.append(static_data)
                    except:
                        print(buff_string+"\tfailed")
                        pass
                try:
                    static_filtered = iterative_chi_filter(stat)
                    static_filt_avg = average_traces(static_filtered)
                    static_prot_only = subtract_unscaled_traces(static_filt_avg, buff_filt_avg)
                    static_vectors[temp][dilution].append(static_prot_only)
                except:
                    print("temp {}C failed for protein".format(temp))

    return static_vectors

def all_off_traces(parent, samp, reps, on_off_map, option=None, multitemp=None, iterations=None, temp=None):
    
    off_vectors = []

    if multitemp:
        for iteration in iterations:

            for n in reps:
                for off in on_off_map.values():

                    off_string = ("{0}/{1}_{2}_{3}_{4}_{5}.tpkl".format(parent, samp, iteration, temp, n, off))
                    try:
                        off_data = parse.parse(off_string)
                        off_data.alg_scale(reference)
                        off_scaled = Trace(off_data.q, np.empty_like(off_data.q), np.empty_like(off_data.q), off_data.scaled_sigSA, off_data.scaled_SA, off_data.Nj)
                        off_vectors.append(off_scaled)
                    except:
                        print(off_string+"\tfailed")

    else:
        for n in reps:
                    for off in on_off_map.values():

                        # off_string = ("{0}/{1}_{2}_{3}_off.tpkl".format(parent, samp, n, off))
                        if option:
                            off_string = ("{0}/{1}_{2}_{3}_on.tpkl".format(parent, samp, n, off))
                        else:
                            off_string = ("{0}/{1}_{2}_{3}.tpkl".format(parent, samp, n, off))
                        try:
                            off_data = parse.parse(off_string)
                            off_data.alg_scale(reference)
                            off_scaled = Trace(off_data.q, np.empty_like(off_data.q), np.empty_like(off_data.q), off_data.scaled_sigSA, off_data.scaled_SA, off_data.Nj)
                            off_vectors.append(off_scaled)
                        except:
                            print(off_string+"\tfailed")

    return off_vectors

def all_vectors(parent, samp, reps, on_off_map, option=None, multitemp=None, iterations=None, temp=None):
    
    all_vectors = []
    all_labels = []
    tr_vectors_labels = []


    if multitemp:
        for iteration in iterations:

            for n in reps:
                # for off in on_off_map.values():
                for on, off in on_off_map.items():
                    on_string = ("{0}/{1}_{2}_{3}_{4}_{5}.tpkl".format(parent, samp, iteration, temp, n, on))
                    off_string = ("{0}/{1}_{2}_{3}_{4}_{5}.tpkl".format(parent, samp, iteration, temp, n, off))
                    try:
                        on_data = parse.parse(on_string)
                        on_data.alg_scale(reference, overwrite=True)

                        off_data = parse.parse(off_string)
                        off_data.alg_scale(reference, overwrite=True)
                        # off_scaled = Trace(off_data.q, np.empty_like(off_data.q), np.empty_like(off_data.q), off_data.scaled_sigSA, off_data.scaled_SA, off_data.Nj)
                        # off_vectors.append(off_scaled)
                        if on_data:
                            if off_data:
                                all_vectors.append(off_data.SA[reference.q>0.03])
                                all_labels.append(off)
                                all_vectors.append(on_data.SA[reference.q>0.03])
                                all_labels.append(on)
                                sub_scaled = subtract_scaled_traces(on_data,off_data)
                                tr_vectors_labels.append((sub_scaled, on))


                    except:
                        print(off_string+"\tfailed")

    # else:
    #     for n in reps:
    #                 for off in on_off_map.values():

    #                     # off_string = ("{0}/{1}_{2}_{3}_off.tpkl".format(parent, samp, n, off))
    #                     if option:
    #                         off_string = ("{0}/{1}_{2}_{3}_on.tpkl".format(parent, samp, n, off))
    #                     else:
    #                         off_string = ("{0}/{1}_{2}_{3}.tpkl".format(parent, samp, n, off))
    #                     try:
    #                         off_data = parse.parse(off_string)
    #                         off_data.alg_scale(reference)
    #                         off_scaled = Trace(off_data.q, np.empty_like(off_data.q), np.empty_like(off_data.q), off_data.scaled_sigSA, off_data.scaled_SA, off_data.Nj)
    #                         off_vectors.append(off_scaled)
    #                     except:
    #                         print(off_string+"\tfailed")

    return all_vectors, all_labels, tr_vectors_labels


def plot_all_traces(samp, trace_lib):
    fig, ax = plt.subplots(figsize=(6, 4),dpi=300)
    for key in trace_lib.keys():
        print("====")
        print("plotting all traces for {}".format(key))
        all_curves = [list(zip(item.q,item.SA)) for item in trace_lib[key]]
        mean_trace = average_traces(trace_lib[key])
        median_SA = np.median([trace.SA for trace in trace_lib[key]],axis=0)

        ### faster plotting
        # ax = plt.axes()
        line_segments = LineCollection(all_curves,color="green",alpha=0.3,label="raw_prefilter")
        ax.add_collection(line_segments)
        ax.plot(mean_trace.q,mean_trace.SA,color="blue",alpha=1.0,label="mean_postfilter")
        ax.fill_between(mean_trace.q, mean_trace.SA+3*mean_trace.sigSA, mean_trace.SA-3*mean_trace.sigSA, facecolor='red', alpha=0.3,label=r"3 $\sigma$")
        # ax.plot(one_curve.q,clean[0],color="blue",alpha=1.0,label="mean_postfilter")
        ax.plot(mean_trace.q,median_SA,color="orange",label="median_prefilter")
        ax.set_ylabel(r'$\Delta I$ (A.U.)')
        ax.set_xlabel(r'q ($\AA^{-1}$)')
        ax.set_xscale("log")
        ax.set_title("{}_{}".format(samp,key))
        ax.legend()
        ### faster plotting
        # ax.set_xscale("log")
        # plt.show()
        fig.tight_layout()
        fig.savefig("{}_{}_cleaned_scaled_TR.png".format(samp,key))
        ax.cla()

    return


def plot_mean_TR_traces(samp, trace_lib):

    fig, ax = plt.subplots(figsize=(6, 4),dpi=300)
    ii = -1
    for key in trace_lib.keys():
        if ii < 0:
            ii=0
            nii = ii
        else:
            N = plt.cm.inferno.N
            ii += int(N/len(trace_lib.keys()))
            nii = N-ii
        print("====")
        print("plotting mean trace for {}".format(key))
        mean_trace = average_traces(trace_lib[key])
        ax.plot(mean_trace.q, mean_trace.SA, label="{}".format(key), color=plt.cm.inferno(nii))
        ax.fill_between(mean_trace.q, mean_trace.SA+3*mean_trace.sigSA, mean_trace.SA-3*mean_trace.sigSA, facecolor=plt.cm.inferno(nii), alpha=0.3)
    handles, labels = fig.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    ax.set_title('{} - Time Resolved Signal'.format(samp))
    ax.set_ylabel(r'$\Delta I$ (A.U.)')
    ax.set_xlabel(r'q ($\AA^{-1}$)')
    ax.set_xscale("log")
    fig.legend(by_label.values(), by_label.keys())
    fig.tight_layout()
    fig.savefig("{}_scaled_TR".format(samp))

    return


def unpack_traces(sampling):
    return[(thing.SA,thing.sigSA) for thing in sampling]

def unpack(packed_trace):
    return(packed_trace.SA,packed_trace.sigSA)

################################################################################


################################################################################
###working version of multitemp march 10th, 2018###
# t0 = clock()

# script,data_dir,buffer_dir= sys.argv

# parent, samp, iterations, temps, reps, on_off_map = sample_map_multitemp(data_dir, multitemp=True)
# filtered_off_vectors = {}
# filtered_vectors = {}
# for temp in temps:
#     subtracted_vectors = time_resolved_traces(parent, samp, reps, on_off_map, multitemp=True, iterations=iterations, temp=temp)
#     filtered_vectors[temp] = {key:iterative_chi_filter(subtracted_vectors[key]) for key in subtracted_vectors.keys()}
#     all_off_vectors = all_off_traces(parent, samp, reps, on_off_map, multitemp=True, iterations=iterations, temp=temp)
#     filtered_off_vectors[temp] = iterative_chi_filter(all_off_vectors)

# with open("filtered_off_vectors_dict.pkl", "wb") as pkl:
#     pickle.dump(filtered_off_vectors, pkl)
# with open("filtered_vectors_dict.pkl", "wb") as pkl:
#     pickle.dump(filtered_vectors, pkl)

# parent2, samp2, iterations2, temps2, reps2, on_off_map2 = sample_map_multitemp(buffer_dir, multitemp=True)
# buffer_filtered_off_vectors = {}
# buffer_filtered_vectors = {}
# for temp2 in temps2:
#     buffer_TR_subtracted_vectors = time_resolved_traces(parent2, samp2, reps2, on_off_map2, multitemp=True, iterations=iterations2, temp=temp2)
#     buffer_filtered_vectors[temp2] = {key:iterative_chi_filter(buffer_TR_subtracted_vectors[key]) for key in buffer_TR_subtracted_vectors.keys()}
#     buffer_all_off_vectors = all_off_traces(parent2, samp2, reps2, on_off_map2, multitemp=True, iterations=iterations2, temp=temp2)
#     buffer_filtered_off_vectors[temp2] = iterative_chi_filter(buffer_all_off_vectors)

# with open("buffer_filtered_off_vectors_dict.pkl", "wb") as pkl:
#     pickle.dump(buffer_filtered_off_vectors, pkl)
# with open("buffer_filtered_vectors_dict.pkl", "wb") as pkl:
#     pickle.dump(buffer_filtered_vectors, pkl)


# avg_filt_off = {temp:average_traces(filtered_off_vectors[temp]) for temp in filtered_off_vectors.keys()}
# for key in avg_filt_off.keys():
#     avg_filt_off[key].buffer_scale(avg_filt_off[key])
# with open("avg_filt_off_dict.pkl", "wb") as pkl:
#     pickle.dump(avg_filt_off, pkl)

# buff_avg_filt_off = {temp:average_traces(buffer_filtered_off_vectors[temp]) for temp in buffer_filtered_off_vectors.keys()}
# for key in buff_avg_filt_off.keys():
#     buff_avg_filt_off[key].buffer_scale(avg_filt_off[key])
# with open("buff_avg_filt_off_dict.pkl", "wb") as pkl:
#     pickle.dump(buff_avg_filt_off, pkl)


# protein_only_avg_filt_off = {temp:buffer_subtract_scaled_traces(avg_filt_off[temp],buff_avg_filt_off[temp]) for temp in filtered_off_vectors.keys()}

# with open("protein_only_avg_filt_off_dict.pkl", "wb") as pkl:
#     pickle.dump(protein_only_avg_filt_off, pkl)


# mean_TR = {temp:{key: subtract_unscaled_traces(average_traces(filtered_vectors[temp][key]),average_traces(buffer_filtered_vectors[temp][key])) for key in filtered_vectors[temp].keys()} for temp in filtered_off_vectors.keys()}
# for temp in mean_TR.keys():
#     for  diff in mean_TR[temp].keys():
#         mean_TR[temp][diff].write_dat(samp+"_"+temp+"_diff_"+diff+".dat")

# with open("mean_TR_dict.pkl", "wb") as pkl:
#     pickle.dump(mean_TR, pkl)

# showme = {temp:{key: add_unscaled_traces(protein_only_avg_filt_off[temp],mean_TR[temp][key]) for key in mean_TR[temp].keys()} for temp in filtered_off_vectors.keys()}

# for temp in showme.keys():
#     for itm in showme[temp].keys():
#         showme[temp][itm].write_dat(samp+"_"+temp+"_"+itm+".dat")

# with open("TR-plus-avg_dict.pkl", "wb") as pkl:
#     pickle.dump(showme, pkl)

# for temp in showme.keys():
#     real_space_plotter(showme[temp],temp)


################################################################################
###SVD analysis###
script,data_dir= sys.argv

parent, samp, iterations, temps, reps, on_off_map = sample_map_multitemp(data_dir, multitemp=True)
multi_all_vectors = {}
multi_all_labels = {}
tr_vectors_labels = {}
# filtered_vectors = {}
for temp in temps:
    multi_all_vectors[temp], multi_all_labels[temp], tr_vectors_labels[temp] = all_vectors(parent, samp, reps, on_off_map, multitemp=True, iterations=iterations, temp=temp)

full_list = multi_all_vectors['19C']
full_labels = multi_all_labels['19C']
# print(full_labels)


fig0, ax0 = plt.subplots()
all_curves = [list(zip(reference.q[reference.q>0.03],item)) for item in full_list]
# print(all_curves[0])
line_segments = LineCollection(all_curves,color="green",lw=0.5)
ax0.add_collection(line_segments)
ax0.plot()
# ax0.scatter(reference.q,full_list)
fig0.savefig("scaled_radavgs.png", dpi=300)
plt.show(block=False)


u,s,v = svd(full_list, full_matrices=False)
fig, ax = plt.subplots()
i = 0
#print("xx shape = {}".format(xx.shape))
for vector in v[0:8]:
    # print vector
    #print("vector shape = {}".format(vector.shape))
    # ax.plot(range(len(vectors)), [value+i for value in vector], "-")
    ax.plot(reference.q[reference.q>0.03], vector+i*0.1, "-", label = "v{}".format(i), lw=0.7)
    i+=1
plt.legend()
ax.set_xscale('log')
#fig.savefig("{}_svd.png".format(run_numb))
fig.savefig("singular_vectors.png", dpi=300)
plt.show(block=False)

#np.save("time_dep_vector", v[2])

fig2, ax2 = plt.subplots()
i = 0
for vector in u.T[0:4]:
    # print vector
    # ax.plot(range(len(vectors)), [value+i for value in vector], "-")
    # x = [i*0.025 for i in range(len(vector))] 
    ax2.plot(vector, label = "v{}".format(i), lw=0.5)
    # ax2.scatter(light, vector[light]+i*.3, marker='+', color='red', edgecolors="none", s=2, label = "v{} light".format(i))
    i+=1
#plt.legend()
    
#fig2.savefig("{}_result.png".format(run_numb))
fig2.savefig("vector_per_image.png", dpi=300)
fig2.set_figwidth(15)
fig3, ax3= plt.subplots()
ax3.plot([np.log(i) for i in s][0:8], "-")
#fig3.savefig("{}_singular_values.png".format(run_numb))
fig3.savefig("singular_values.png")
plt.show(block=False)
#plt.show(figsize(10,10),dpi=300)
    # print i
    # print ordered_keylist
#fig2.show()
fig4, ax4 = plt.subplots()
i = 0

time_resolved_vectors = {}
for vector in u.T[0:8]:
    for time in TIMES:
        time_resolved_vectors[time] = np.mean(np.array(vector[full_labels.index(time)]))
        ax4.scatter(parse.times_numeric(time),np.mean(np.subtract(np.array(vector[full_labels.index(time)]), np.array(vector[full_labels.index(time)-1]))), color="black", label=time)
    # print vector
    # ax.plot(range(len(vectors)), [value+i for value in vector], "-")
    # x = [i*0.025 for i in range(len(vector))] 
        # ax4.hist(vector[full_labels.index(time)], 100, color='blue', alpha=0.5, label = "v{}".format(str(i)+'_'+str(time)))
    # ax4.hist(vector[light], 500, color='red', alpha=0.5, label = "v{} light".format(i))
    ax4.set_xscale('log')
    ax4.set_xlabel('Time (ns)')
    # plt.legend()
    fig4.savefig("v{}_time_dependence.png".format(i), dpi=300)
    # plt.show()
    
    i+=1
    ax4.cla()
plt.show()