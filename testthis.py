def progress_bar(step, final):
    print('|'+'-'*(step-1) + '>' + ' '*(final-step)+'|  {:2}/{:2}     '.format(step, final), end = '')

passed = 0
failed = 0
fail_list = []

print('----------------------------------------------------------')
print('MAGNA-U Test')
print('----------------------------------------------------------')
print('\n', 'Testing Dependencies...', '\n')

dependencies = ['magna.utils', 'ubermag', 'oommfc', 'discretisedfield', 'micromagneticmodel', 'micromagneticdata', 'matplotlib',
                'matplotlib.pyplot', 'k3d', 'numpy', 'pandas', 'csv', 'random', 'ast', 'time', 'os', 'sys', 'cv2', 'networkx']

for dependency in dependencies:
    progress_bar(dependencies.index(dependency)+1, len(dependencies))
    try:
        exec('import '+dependency)
        print('\033[0;32mImport {}: PASSED\033[0;0m'.format(dependency))
        passed += 1
    except ModuleNotFoundError:
        print('\033[0;31mImport {}: FAILED\033[0;0m'.format(dependency))
        failed =+1
        fail_list.append('Import '+dependency)

import os
import sys
import traceback
import matplotlib
matplotlib.use('Agg')
import magna.utils as mu

run_dir = './MAGNA-U_TEST'
if not os.path.isdir(run_dir):
    os.mkdir(run_dir)

print('-'*40)
print("Testing utils.py")

checks = {'Create an MNP': "mnp = mu.MNP(0, name='test', directory=run_dir, layer_radius=1, discretizations=(2,2,2))",
          'Initialize an MNP': "mnp.initialize(autosave=False)",
          'Save MNP Data': "mu.save_mnp(mnp)",
          'Save MNP Fields': "mnp.save_fields()",
          'Load an MNP': "mnp = mu.load_mnp(0, name='test', filepath=run_dir)",
          'Load MAKU Fields': "mnp.m_field, mnp.a_field, mnp.k_field, mnp.u_field = mnp.load_fields()",
          'Create MNP_System': "system = mu.MNP_System(mnp)",
          'Initialize MNP_System': "system.initialize(mnp)",
          'Create MNP_MinDriver': 'md = mu.MNP_MinDriver()',
          'Drive MNP_System':"md.drive_system(system)",
          'Create MNP_Analyzer':"plotter = mu.MNP_Analyzer(mnp)",
          'XY Plot': "plotter.xy_plot()",
          'Z Plot' : "plotter.z_plot()",
          'XY Scalar Plot' : "plotter.xy_scalar_plot()",
          'Z Scalar Plot': "plotter.z_scalar_plot()",
          'Extract': "plotter.extract()",
          'MNP Center Vectors Plot': "plotter.mpl_center_vectors()",
          'Quick Drive': "mnp = mu.MNP(1, name='test', directory=run_dir, layer_radius=1, discretizations=(2,2,2))\nmu.quick_drive(mnp)",
          'Hysteresis': "mnp = mu.MNP(2, name='test', directory=run_dir, layer_radius=1, discretizations=(2,2,2))\nhd=mu.MNP_HysteresisDriver()\nhd.drive_hysteresis(mnp, n=3)",
          'Create MNP_Hysteresis_Analyzer': "hyst_plotter = mu.MNP_Hysteresis_Analyzer(mnp)",
          'Hysteresis Loop Plot': "hyst_plotter.hyst_loop_plot()",
          'Hysteresis Step Plots': "hyst_plotter.hyst_steps_plot(type='z')",
          'Hysteresis Movie': "hyst_plotter.hyst_movie()",
          'Create MNP_Domain_Analyzer': "dom_plotter = mu.MNP_Domain_Analyzer(mnp, preload_field=True)",
          'Find Domain Regions': "dom_plotter.find_regions()",
          'Save Domain Data': "dom_plotter.save_domains()"
          }

for n in range(len(checks)):
    check = list(checks.keys())[n]
    progress_bar(n+1, len(checks))
    try:
        sys.stdout = open(os.devnull, 'w')
        exec(checks.get(check))
        sys.stdout = sys.__stdout__
        print('\033[0;32m{}: PASSED\033[0;0m'.format(check))
        passed += 1
    except Exception:
        sys.stdout = sys.__stdout__
        print('\033[0;31m{}: FAILED\033[0;0m'.format(check))
        traceback.print_exc()
        failed += 1
        fail_list.append(check)

print('-'*40+'\n')
print('TEST SUMMARY')
print('\n')
print('\033[0;32mPASSED: {}\033[0;0m'.format(passed))
print('\033[0;31mFAILED: {}\033[0;0m'.format(failed))

if failed==0:
    print('Test Complete... SUCCESS!')
    os.system('rm -r MAGNA-U_TEST')
    os.system('rm -r DELETE')
else:
    print('Failures: ',fail_list)