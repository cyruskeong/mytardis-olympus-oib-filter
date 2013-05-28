from fractions import Fraction
import logging
#import logging.handlers

from tardis.tardis_portal.models import Schema, DatafileParameterSet
from tardis.tardis_portal.models import ParameterName, DatafileParameter
import subprocess
import tempfile
import base64
import struct
import binascii
import os

logger = logging.getLogger(__name__)

class OlympusoibImageFilter(object):


    """If a white list is specified then it takes precidence and all
    other tags will be ignored.

    :param name: the short name of the schema.
    :type name: string
    :param schema: the name of the schema to load the EXIF data into.
    :type schema: string
    :param tagsToFind: a list of the tags to include.
    :type tagsToFind: list of strings
    :param tagsToExclude: a list of the tags to exclude.
    :type tagsToExclude: list of strings
    """
    def __init__(self, name, schema, metadata_path, tagsToFind=[], tagsToExclude=[]):
        self.name = name
        self.schema = schema
        self.metadata_path = metadata_path
        self.tagsToFind = tagsToFind
        self.tagsToExclude = tagsToExclude
	logger.error('Olympus-init()')
	logger.debug('initialising OlympusoibImageFilter')

    def __call__(self, sender, **kwargs):
        """post save callback entry point.
        logger.debug('Olympus-init()')
        :param sender: The model class.
        :param instance: The actual instance being saved.
        :param created: A boolean; True if a new record was created.
        :type created: bool
        """
        logger.error('Olympus-call()')
        instance = kwargs.get('instance')

        schema = self.getSchema()

        filepath = instance.get_absolute_filepath()

        raw_fname = filepath

        """:only process Olympus oib files"""
        if not filepath.endswith('.oib'):
            return None

        try:

            logger.error('Olympus-oib image found')	
            #handle Olympus files
           
            metadata_dump = dict()
            tags = dict()

            ###############################################################################
            # explore some nitime timeseries features
            logger.error('step 1')	
            logger.error(self.metadata_path)
            		
            bin_infopath = os.path.basename(self.metadata_path)
          
            cd_infopath = os.path.dirname(self.metadata_path)
            
            image_information = self.textoutput(cd_infopath, bin_infopath,
                                                          filepath, '-info').split('\n')[0:]
            
            logger.error(image_information)
            logger.error('step 1.0.0')
            info = image_information
            
            logger.error('step 1.0.1')
            for infolist in info:
                if infolist !='':
                   
                    logger.error('step 1.0.2')
                    metaname=infolist.split(":")[0]
                    logger.error(metaname)
                    logger.error('  ||         step 1.0.3')
                    metavalue=infolist.split(":")[1]
                    logger.error(metavalue)
                    logger.error('step 1.0.4')
                    tags[metaname]=metavalue
            
            logger.error('step 1.0')
            logger.error(tags)
           # logger.error('image_info' & image_information)

            # DimensionOrder
            metadata_dump['dimensionOrder'] = tags['dimensions']
            metadata_dump['physicalSizeX'] = tags['xRes']
            metadata_dump['physicalSizeY'] = tags['yRes']
            metadata_dump['sizeZ'] = tags['zsize']
            metadata_dump['sizeT'] = tags['tsize']
            metadata_dump['pages'] = tags['pages']
            metadata_dump['channels'] = tags['channels']
            metadata_dump['width'] = tags['width']
            metadata_dump['height'] = tags['height']
         
            logger.error('step 1.1')
            info = self.textoutput(cd_infopath, bin_infopath,
                                                        filepath, '-metaparsed').split('\n')[0:]
            logger.error('step 1.1.1')
            logger.error(info)
            
            for infolist in info:
                           if infolist !='':
                              
                               logger.error('step 1.1.2')
                               metaname=infolist.split(":")[0]
                               logger.error(metaname)
                               logger.error('step 1.1.3')
                               metavalue=infolist.split(":")[1]
                               logger.error(metavalue)
                               logger.error('step 1.1.4')
                               tags[metaname]=metavalue
            

            logger.error('step 1.2')
            #metadata_dump['sizeP'] = tags['image_num_p']
            #metadata_dump['acquisition_date'] = tags['date_time']
           
            # get file id logger.error('image_information ' + raw.info['file_id'])
            metadata_dump['oib_information'] = 'Some fixed value'
	           

            logger.error('step 2')
            ###############################################################################

            #Plot graph 
           
            logger.error('step 2.1')

          
            logger.error('step 2.2')

          
            logger.error('step 2.3')

           
            #pl.savefig('/opt/mytardis/data/staging/test1.png')
     
            logger.error('step 2.4')

            #previewImage64 = self.base64_encode_file('/opt/mytardis/data/staging/test1.png')
            #os.remove(outputfilename)
            logger.error('step 2.5')
           # if previewImage64:
            #    metadata_dump['previewImage'] = previewImage64               
  
            logger.error('step 2.6')
            self.saveMetadata(instance, schema, metadata_dump)

        except Exception, e:
            logger.debug(e)
            return None

    def saveMetadata(self, instance, schema, metadata):
        """Save all the metadata to a Dataset_Files parameter set.
        """
	logger.error('Olympus-saveMetadata()')
        parameters = self.getParameters(schema, metadata)

        if not parameters:
            return None

        try:
            ps = DatafileParameterSet.objects.get(schema=schema,
                                                  dataset_file=instance)
            return ps  # if already exists then just return it
        except DatafileParameterSet.DoesNotExist:
            ps = DatafileParameterSet(schema=schema,
                                      dataset_file=instance)
            ps.save()

	for p in parameters:
            print p.name
            if p.name in metadata:
                dfp = DatafileParameter(parameterset=ps,
                                        name=p)
                if p.isNumeric():
                    if metadata[p.name] != '':
                        dfp.numerical_value = metadata[p.name]
                        dfp.save()
                else:
                    print p.name
                    if isinstance(metadata[p.name], list):
                        for val in reversed(metadata[p.name]):
                            strip_val = val.strip()
                            if strip_val:
                                if not strip_val in exclude_line:
                                    dfp = DatafileParameter(parameterset=ps,
                                                            name=p)
                                    dfp.string_value = strip_val
                                    dfp.save()
                    else:
                        dfp.string_value = metadata[p.name]
                        dfp.save()

        return ps

    def getParameters(self, schema, metadata):
        """Return a list of the paramaters that will be saved.
        """
        logger.error('Olympus-getParameters()')
	param_objects = ParameterName.objects.filter(schema=schema)
        parameters = []
        for p in metadata:

            if self.tagsToFind and not p in self.tagsToFind:
                continue

            if p in self.tagsToExclude:
                continue

            parameter = filter(lambda x: x.name == p, param_objects)

            if parameter:
                parameters.append(parameter[0])
                continue

            # detect type of parameter

 		datatype = ParameterName.STRING

            # Int test
            try:
                int(metadata[p])
            except ValueError:
                pass
            except TypeError:
                pass
            else:
                datatype = ParameterName.NUMERIC

            # Fraction test
            if isinstance(metadata[p], Fraction):
                datatype = ParameterName.NUMERIC

            # Float test
            try:
                float(metadata[p])
            except ValueError:
                pass
            except TypeError:
                pass
            else:
                datatype = ParameterName.NUMERIC

        return parameters

    def getSchema(self):
        """Return the schema object that the paramaterset will use.
        """
        logger.error('Olympus-getSchema()')
        try:
            return Schema.objects.get(namespace__exact=self.schema)
        except Schema.DoesNotExist:
            schema = Schema(namespace=self.schema, name=self.name,
                            type=Schema.DATAFILE)
            schema.save()
            return schema

    def base64_encode_file(self, filename):
        """encode file from filename in base64
        """
        logger.error('Olympus-base64_encode_file()')
        with open(filename, 'r') as fileobj:
            read = fileobj.read()
            encoded = base64.b64encode(read)

	return encoded

    def exec_command(self, cmd):
        """execute command on shell
        """
        logger.error('Olympus-exec_command()')
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            shell=True)

        p.wait()

        result_str = p.stdout.read()

        return result_str

    def fileoutput(self, cd, execfilename, inputfilename, outputfilename, args=""):
        """execute command on shell with a file output
        """
        logger.error('Olympus-fileoutput()')
        cmd = "cd '%s'; ./'%s' '%s' '%s' %s" %\
            (cd, execfilename, inputfilename, outputfilename, args)
        print cmd

        return self.exec_command(cmd)
    
    def parse_output(self, output):
        metadata = []
        for line in output:
            term = self.parse_term(line)
            value = self.parse_value(line)
    
            try:
                value_outputs = self.values[term](term, value)
    
                if type(value_outputs) is list:
    
                    for value_output in value_outputs:
    
                        metadata.append(value_output)
                else:
                    metadata.append(value_outputs)
    
            except KeyError:
                logger.debug('no ' + str(term) + ' found')
    
        return metadata
    
    
    def textoutput(self, cd, execfilename, inputfilename, args=""):
        """execute command on shell with a stdout output
        """
        logger.error('Olympus-textoutput()')
        cmd = "cd '%s'; ./'%s' '-i' '%s' %s" %\
            (cd, execfilename, inputfilename, args)
        print cmd

        return self.exec_command(cmd)

def make_filter(name='', schema='', tagsToFind=[], tagsToExclude=[]):
    logger.error('Olympus-make_filter()')
    if not name:
        raise ValueError("OlympusoibImageFilter "
                         "requires a name to be specified")
    if not schema:
        raise ValueError("OlympusoibImageFilter "
                         "requires a schema to be specified")
    return OlympusoibImageFilter(name, schema, tagsToFind, tagsToExclude)
make_filter.__doc__ = OlympusoibImageFilter.__doc__



