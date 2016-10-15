# Copyright(c) 2016 Cloudflare, Inc. All rights reserved.
# Cloudflare, Inc. Confidential and Proprietary.

# Import python stdlib

# Import third party modules
from probes import get_server

# Import Arista modules
import Cell
import BasicCli
import CliParser
import ConfigMount
import HostnameCli

from CliModel import Model

probesConfig = None
# probesServer = None

PROBES_DEFAULTS = {
    'source': 'lo0',
    'count': 1,
    'interval': 1,
    'type': 'icmp'
}

tokenShowProbes = CliParser.KeywordRule( 'probes',
    helpdesc='Arista Probes' )

tokenShowProbesConfig = CliParser.KeywordRule(
   'config',
   helpdesc='Configuration of Arista probes' )

tokenShowProbesResults = CliParser.KeywordRule(
    'results',
    helpdesc='Results of Arista probes' )

### Operational commands

class GetProbesConfig( Model ):
    def render( self ):
        print(probesConfig)

class GetProbesResults( Model ):
    def render( self ):
        print 'Will display probes results.'

def doShowProbesConfig( mode ):
    probes_config = GetProbesConfig()
    return probes_config.render()


def doShowProbesResults( mode ):
    probes_results = GetProbesResults()
    return probes_results.render()

BasicCli.registerShowCommand( tokenShowProbes, tokenShowProbesConfig, doShowProbesConfig )
BasicCli.registerShowCommand( tokenShowProbes, tokenShowProbesResults, doShowProbesResults )

### Configuration commands
# ------------------------------------------
# Probes config commands:
#    no probes
#    no probes probe-name <name>
#    no probes probe-name <name> test <name>
#    probes probe-name <name> test <name> [source <source>] target <target> [count <count>] [interval <interval>] [type <type>]
#    no probes probe-name <name> test <name> [source <source>] target <target> [count <count>] [interval <interval>] [type <type>]
# from global config mode

tokenConfigProbes = CliParser.KeywordRule(
   'probes',
   helpdesc='Configure Probes' )

tokenProbeNameKnob = CliParser.KeywordRule(
   'probe-name',
   helpdesc='Specify a name for a specific probe' )

probeNameRe = '[^\s]+'
tokenProbeName = CliParser.PatternRule( probeNameRe,
                                        name='probeName',
                                        helpname='<name>',
                                        helpdesc='Name of the probe' )

tokenTestKnob = CliParser.KeywordRule(
   'test',
   helpdesc='Specify a test name' )

testNameRe = '[^\s]+'
tokenTestName = CliParser.PatternRule( testNameRe,
                                       name='testName',
                                       helpname='<name>',
                                       helpdesc='Name of the test' )


tokenTestSource = CliParser.KeywordRule(
   'source',
   helpdesc='Source IP Address' )

tokenSourceIpAddrOrHostname = HostnameCli.IpAddrOrHostnameRule(
   helpname="<ip addr>",
   helpdesc="Source IP Address",
   name='ipAddrOrHostname',
   ipv6=True )

tokenTarget = CliParser.KeywordRule(
   'target',
   helpdesc='Target IP Address' )

tokenTargetIpAddrOrHostname = HostnameCli.IpAddrOrHostnameRule(
   helpname="<ip addr>",
   helpdesc="Target IP Address",
   name='ipAddrOrHostname',
   ipv6=True )

tokenType = CliParser.KeywordRule(
   'type',
   helpdesc='Type of probe config: TCP/UDP/ICMP/ICMP6' )

probeTypes = { 'icmp': 'icmp', 'icmp6': 'icmp6', 'tcp': 'tcp', 'udp': 'udp' }
probeTypeMatcher = CliParser.DynamicKeywordsMatcher(
         lambda mode: probeTypes,
         emptyTokenCompletion=[ CliParser.Completion(
              '<probe type>', 'Choose between: icmp, icmp6, tcp, upd',
               literal=False ) ] )

monthRule = CliParser.TokenRule( matcher=probeTypeMatcher, name='type',
                                 value=lambda mode, match: probeTypes[ match ] )

tokenCount = CliParser.KeywordRule(
   'count',
   helpdesc='Number of probes per test: between 1 and 15' )

countNumberRule = CliParser.RangeRule( 1, 15,
                                       name='count',
                                       helpdesc='Number of probes per test: between 1 and 15' )

tokenInterval = CliParser.KeywordRule(
   'interval',
   helpdesc='Delay between two tests: between 1 and 86400 secondsz' )

intervalNumberRule = CliParser.RangeRule( 1, 86400,
                                          name='count',
                                          helpdesc='Number of probes per test: between 1 and 15' )


def doDisableProbes( mode ):
    print('Will disable probes config')
    probesConfig = {}


def doDeleteProbeName( mode, probeName, options=None ):
    print 'Will delete probe {}'.format(probeName)
    if probeName in probesConfig.keys():
        probesConfig.pop(probeName)


def doDeleteProbeTestConfig( mode, probeName, testName, options=None ):
    print 'Will delete {0}, under probe {1} with options {2}'.format(
        testName,
        probeName,
        str(options)
    )

    if probeName in probesConfig.keys():
        if testName in probesConfig[probeName].keys():
            if not options:
                probesConfig[probeName].pop(testName)
            else:
                opts_dict = dict(options)
                opts_dict.pop('target', None)  # cant remove the target
                for opt in opts_dict.keys():
                    probesConfig[probeName][testName][opt] = PROBES_DEFAULTS[opt]

    print(probesConfig)

def doConfigProbeTest( mode, probeName, testName, ipAddrOrHostname, options=None ):
    print 'Will configure test {0}, under probe {1} with options {2}'.format(
        testName,
        probeName,
        str(options)
    )

    if probeName not in probesConfig.keys():
        probesConfig[probeName] = {}
    if testName not in probesConfig[probeName].keys():
        probesConfig[probeName][testName] = PROBES_DEFAULTS.copy()

    probesConfig[probeName][testName]['target'] = ipAddrOrHostname

    opts_dict = dict(options)
    for opt, val in opts_dict.iteritems():
        probesConfig[probeName][testName][opt] = val

    print(probesConfig)

# remove the whole config of the probes
BasicCli.GlobalConfigMode.addCommand(
   ( BasicCli.noOrDefault, tokenConfigProbes, doDisableProbes ) )

# remove the config of a specific probe
BasicCli.GlobalConfigMode.addCommand(
   ( BasicCli.noOrDefault, tokenConfigProbes, tokenProbeNameKnob, tokenProbeName,
     doDeleteProbeName ) )

# remove config of a specific test - either details and use defaults, either whole test
BasicCli.GlobalConfigMode.addCommand(
   ( BasicCli.noOrDefault, tokenConfigProbes, tokenProbeNameKnob, tokenProbeName, tokenTestKnob, tokenTestName,
     CliParser.SetRule(
         ( '>>source', tokenTestSource ),
         ( '>>count', tokenCount ),
         ( '>>interval', tokenInterval ),
         ( '>>type', tokenType ),
         name='options' ),
     doDeleteProbeTestConfig ) )

# configure one more test under a specific probe name
BasicCli.GlobalConfigMode.addCommand(
   ( tokenConfigProbes, tokenProbeNameKnob, tokenProbeName, tokenTestKnob, tokenTestName, tokenTarget, tokenTargetIpAddrOrHostname,
     CliParser.SetRule(
         ( '>>source', tokenTestSource, tokenSourceIpAddrOrHostname ),
         ( '>>count', tokenCount, countNumberRule ),
         ( '>>interval', tokenInterval, intervalNumberRule ),
         ( '>>type', tokenType, monthRule ),
         name='options' ),
     doConfigProbeTest ) )

# Plugin definition
def Plugin( entityManager ):
    global probesConfig
    global probesServer

    # probesServer = get_server()
    # probesConfig = probesServer.get_config()
    probesConfig = {}
    # probesConfig = ConfigMount.mount(
    #     entityManager, "probes/config", "Probes::Config", "w" )
