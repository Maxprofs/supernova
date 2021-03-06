import subprocess
import os
import shutil
import glob
import tenkit.supernova.alerts as alerts
import tenkit.supernova.plot as plot
import martian

def split(args):
    mem_gb = 2048
    threads = 28
    chunk_defs = [{'__mem_gb': mem_gb, '__threads':threads, '__special': 'asmlarge' }]
    return {'chunks': chunk_defs}

def join(args, outs, chunk_defs, chunk_outs):
    shutil.move(chunk_outs[0].default, outs.default)
    summary_cs = os.path.join(outs.default, "stats", "summary_cs.csv")
    report     = os.path.join(outs.default, "stats", "summary.txt")
    shutil.copy( summary_cs, outs.summary_cs )
    shutil.copy( report, outs.report )

def log_dmesg( ):
    num_lines = 100
    try:
        dmesg_out = subprocess.check_output( ["dmesg"] )
        martian.log_info( "----dmesg output----" )
        dmesg_lines = dmesg_out.split("\n")
        if len(dmesg_lines) <= num_lines:
            martian.log_info( dmesg_out )
        else:
            for line in dmesg_lines[-num_lines:]:
                martian.log_info( line )
        martian.log_info( "--------------------" )
    except Exception as e:
        martian.log_info( "Unable to run dmesg." )
        martian.log_info( str(e) )

def log_ps( ):
    MAX_LINES = 6
    ps_cmd = ["ps", "--sort=-rss", "-eo", "pid,pmem,rss,comm,uid"]
    ps_log = "Running command " + " ".join(ps_cmd) + "\n"
    try:
        ps_out = subprocess.check_output( ps_cmd )
        for i, line in enumerate( ps_out.split("\n") ):
            if i == MAX_LINES:
                break
            ps_log += "%8s %5s %12s %5.5s %s\n" % tuple(line.split())
    except:
        ps_log += "Running ps command failed\n"
    martian.log_info( ps_log )

def process_return_code( returncode ):    
    msg = None
    if returncode < 0:
        SIG_DICT = { -9: "KILL signal",
                     -1: "HUP signal",
                     -2: "INT signal",
                     -15: "TERM signal" }
        sig_name = SIG_DICT.get( returncode, "signal" )
        msg = "A Supernova process was terminated with a %s "\
        "(code: %d). This may have been sent by you, your IT admin, "\
        "or automatically by the system itself "\
        "(e.g. the out-of-memory killer)." % (sig_name,-returncode)
    elif returncode == 99:
        msg = "Supernova terminated because of insufficient memory. "\
        "The stage _stdout file may contain additional useful information, "\
        "e.g., whether any competing processes were running."
    return msg

def main(args, outs):
    print "__threads=",args.__threads
    print "__mem_gb=",args.__mem_gb
    input_dir = os.path.join(args.parent_dir,"a.base")

    cp_command = ['CP','DIR='+input_dir, 'MAX_MEM_GB='+str(args.__mem_gb), 'NUM_THREADS='+str(args.__threads)]

    if args.known_sample_id is not None:
        cp_command.append( "SAMPLE={}".format(args.known_sample_id) )
    if args.sample_id is not None:
        cp_command.append( "CS_SAMPLE_ID={}".format(args.sample_id) )
    if args.sample_desc is not None:
        cp_command.append( "CS_SAMPLE_DESC={}".format(args.sample_desc) )
    if args.addin is not None and "CP" in args.addin:
        cp_command.extend(args.addin["CP"].split())
    if args.nodebugmem is None or not args.nodebugmem:
        cp_command.append( "TRACK_SOME_MEMORY=True" )


    ## write alerts
    alerts.write_stage_alerts("cp", path=args.parent_dir)

    alarm_bell = alerts.SupernovaAlarms(base_dir=args.parent_dir)
    try:
        subprocess.check_call( cp_command )
    except subprocess.CalledProcessError as e:
        alarm_bell.post()
        ## if we actually reach this point
        ## it means that Martian::exit() was not called from C++.
        
        ## log dmesg
        log_dmesg( )

        ## log ps output
        log_ps( )

        ## detect return code
        exit_msg = process_return_code( e.returncode )
        alarm_bell.exit(exit_msg)
 
    ## post any warnings from this stage here
    alarm_bell.post()

    ## make plots
    plot.try_plot_molecule_hist(args)
    plot.try_plot_kmer_spectrum(args)
    
    shutil.move( args.parent_dir, outs.default )
    for f in glob.glob("*.mm"):
        shutil.move(f, os.path.join(outs.default,"stats") )
