# -*- coding: utf-8 -*-

"""
Test wind scenarios.
"""

from __future__ import print_function
from scipy import allclose
                
from core_hazimp import hazimp            
import unittest
import os
import tempfile
import numpy
#from __future__ import print_function

from scipy import allclose
                
from core_hazimp import hazimp                
from core_hazimp import misc

from core_hazimp.jobs.jobs import LOADRASTER, LOADCSVEXPOSURE, \
    LOADXMLVULNERABILITY, SIMPLELINKER, SELECTVULNFUNCTION, \
    LOOKUP, SAVEALL
from core_hazimp.calcs.calcs import STRUCT_LOSS
from core_hazimp.config import LOADWINDTCRM, TEMPLATE, WINDV1, SAVE

class TestWind(unittest.TestCase): 
    """
    Test the calcs module
    """

    def test_const_test(self):
        # First test running an end to end cyclone test based 
        # on a config dictionary, template default'
        
        # The output file
        f = tempfile.NamedTemporaryFile(
            suffix='.npz', 
            prefix='HAZIMPt_wind_scenarios_test_const',
            delete=False)
        
        wind_dir = os.path.join(misc.EXAMPLE_DIR, 'wind')
        exp_filename = os.path.join(wind_dir, 
                                    'small_exposure_tcrm.csv')
        wind_filename = os.path.join(wind_dir, 'gust01.txt')
        vul_filename = os.path.join(misc.RESOURCE_DIR, 
                                    'domestic_wind_vul_curves.xml')
        config = {
            'jobs':[LOADCSVEXPOSURE, LOADRASTER, LOADXMLVULNERABILITY,
            SIMPLELINKER, SELECTVULNFUNCTION, LOOKUP, STRUCT_LOSS,
            SAVEALL],
            LOADCSVEXPOSURE:{'exposure_file':exp_filename,
                                 'exposure_latitude':'latitude',
                                 'exposure_longitude':'longitude'},
            LOADRASTER:{'file_list':[wind_filename],
                        'attribute_label':
                            '0.2s gust at 10m height m/s'},
            LOADXMLVULNERABILITY:{'vulnerability_file':vul_filename},
            SIMPLELINKER:{'vul_functions_in_exposure':{
                    'domestic_wind_2012':'wind_vulnerability_model'}},
            SELECTVULNFUNCTION:{'variability_method':{
                    'domestic_wind_2012':'mean'}},
            SAVEALL:{'file_name':f.name}}
            
        context = hazimp.main(config_dic=config)
        self.assertTrue(allclose(
                context.exposure_att['structural_loss'],
                context.exposure_att['calced-loss']))
        
        exp_dict = numpy.load(f.name)
        self.assertTrue(allclose(exp_dict['structural_loss'],
                                 exp_dict['calced-loss']))
        os.remove(f.name)
        
        

    def test_wind_v1_template(self):
        # Test running an end to end cyclone test based 
        # on a wind config template.
        
        # The output file
        f = tempfile.NamedTemporaryFile(
            suffix='.npz', 
            prefix='HAZIMPt_wind_scenarios_test_const',
            delete=False)
        
        wind_dir = os.path.join(misc.EXAMPLE_DIR, 'wind')
        exp_filename = os.path.join(wind_dir, 
                                    'small_exposure_tcrm.csv')
        wind_filename = os.path.join(wind_dir, 'gust01.txt')
        config = {
            TEMPLATE:WINDV1,
            LOADCSVEXPOSURE:{'exposure_file':exp_filename,
                                 'exposure_latitude':'latitude',
                                 'exposure_longitude':'longitude'},
            LOADWINDTCRM:[wind_filename],
            SAVE:f.name}
            
        context = hazimp.main(config_dic=config)
        self.assertTrue(allclose(
                context.exposure_att['structural_loss'],
                context.exposure_att['calced-loss']))
        
        exp_dict = numpy.load(f.name)
        self.assertTrue(allclose(exp_dict['structural_loss'],
                                 exp_dict['calced-loss']))
        os.remove(f.name)
        
    def test_wind_yaml(self):
        # Test running an end to end cyclone test based 
        # on a wind config template.
        
        wind_dir = os.path.join(misc.EXAMPLE_DIR, 'wind')
        exp_filename = os.path.join(wind_dir, 
                                    'small_exposure_tcrm.csv')
        wind_filename = os.path.join(wind_dir, 'gust01.txt')
        
        # The output file
        f_out = tempfile.NamedTemporaryFile(
            suffix='.npz', 
            prefix='HAZIMPt_wind_scenarios_test_const',
            delete=False)
                
        # The config file
        f = tempfile.NamedTemporaryFile(
            suffix='.yaml', 
            prefix='HAZIMPt_wind_scenarios_test_const',
            delete=False)
        
        print(TEMPLATE + ': ' +WINDV1, file=f)
        print(LOADCSVEXPOSURE + ':', file=f)
        print('  exposure_file: ' + exp_filename, file=f)
        print('  exposure_latitude: latitude', file=f)
        print('  exposure_longitude: longitude', file=f)
        print(LOADWINDTCRM + ': [' + wind_filename + ']', file=f)
        print(SAVE + ': ' + f_out.name, file=f)
        f.close()
        
        context = hazimp.main(config_file=f.name)
        self.assertTrue(allclose(
                context.exposure_att['structural_loss'],
                context.exposure_att['calced-loss']))
        
        exp_dict = numpy.load(f_out.name)
        self.assertTrue(allclose(exp_dict['structural_loss'],
                                 exp_dict['calced-loss']))
        os.remove(f.name)
        os.remove(f_out.name)
#-------------------------------------------------------------
if __name__ == "__main__":
    
    SUITE = unittest.makeSuite(TestWind,'test')
    #SUITE = unittest.makeSuite(TestWind,'test_wind_yaml')
    RUNNER = unittest.TextTestRunner()
    RUNNER.run(SUITE)
