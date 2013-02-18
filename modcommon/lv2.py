import rdflib, os
from . import rdfmodel as model

lv2core = rdflib.Namespace('http://lv2plug.in/ns/lv2core#')
doap = rdflib.Namespace('http://usefulinc.com/ns/doap#')
epp = rdflib.Namespace('http://lv2plug.in/ns/dev/extportinfo#')

units = rdflib.Namespace('http://lv2plug.in/ns/extensions/units#')

class Bundle(model.Model):
    
    plugins = model.ModelSearchField(lv2core.Plugin, 'Plugin')

    def __init__(self, path):
        super(Bundle, self).__init__()
        self.parse(os.path.join(path, 'manifest.ttl'))
        self.parse('units.ttl') 

class Plugin(model.Model):

    url = model.IDField()
    name = model.StringField(doap.name)
    binary = model.FileField(lv2core.binary)
    maintainer = model.InlineModelField(doap.maintainer, 'Foaf')
    developer = model.InlineModelField(doap.developer, 'Foaf')
    license = model.StringField(doap.license, lambda x: x.split('/')[-1])

    microVersion = model.IntegerField(lv2core.microVersion)
    minorVersion = model.IntegerField(lv2core.minorVersion)

    order = lambda x: x['index']
    audio_input_ports = model.ListField(lv2core.port, model.InlineModelField, 'Port', order=order,
                                        accepts=[lv2core.AudioPort, lv2core.InputPort])
    audio_output_ports = model.ListField(lv2core.port, model.InlineModelField, 'Port', order=order,
                                         accepts=[lv2core.AudioPort, lv2core.OutputPort])

    control_input_ports = model.ListField(lv2core.port, model.InlineModelField, 'ControlInputPort', order=order,
                                          accepts=[lv2core.ControlPort, lv2core.InputPort])
    
    control_output_ports = model.ListField(lv2core.port, model.InlineModelField, 'Port', order=order,
                                           accepts=[lv2core.ControlPort, lv2core.OutputPort])

    #category = model.

    def extract_data(self):
        super(Plugin, self).extract_data()
        d = self.data
        d['ports'] = { 'audio': {}, 'control': {} }
        d['ports']['audio']['input'] =    d.pop('audio_input_ports')
        d['ports']['audio']['output'] =   d.pop('audio_output_ports')
        d['ports']['control']['input'] =  d.pop('control_input_ports')
        d['ports']['control']['output'] = d.pop('control_output_ports')

class Port(model.Model):
    symbol = model.StringField(lv2core.symbol)
    name = model.StringField(lv2core.name)
    index = model.IntegerField(lv2core['index'])

class ControlInputPort(Port):
    default = model.FloatField(lv2core.default)
    minimum = model.FloatField(lv2core.minimum)
    maximum = model.FloatField(lv2core.maximum)

    unit = model.InlineModelField(units.unit, 'Unit')

    toggled = model.BooleanPropertyField(lv2core.portProperty, lv2core.toggled)
    enumeration = model.BooleanPropertyField(lv2core.portProperty, lv2core.enumeration)
    logarithmic = model.BooleanPropertyField(lv2core.portProperty, epp.logarithmic)
    integer = model.BooleanPropertyField(lv2core.portProperty, lv2core.integer)
    enumeration = model.BooleanPropertyField(lv2core.portProperty, lv2core.integer)
    scalePoints = model.ListField(lv2core.scalePoint, model.InlineModelField, 'ScalePoint', order=lambda x:x['value'])

class Unit(model.Model):
    label = model.StringField(model.rdfschema.label)
    render = model.StringField(units.render)
    symbol = model.StringField(units.symbol)

class ScalePoint(model.Model):
    label = model.StringField(model.rdfschema.label)
    value = model.FloatField(model.rdfsyntax.value)

class Foaf(model.Model):
    foaf = rdflib.Namespace('http://xmlns.com/foaf/0.1/')

    name = model.StringField(foaf.name)
    mbox = model.StringField(foaf.mbox, modifier = lambda x: x.replace('mailto:', ''))
    homepage = model.StringField(foaf.homepage)

