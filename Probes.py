# Copyright(c) 2016 Cloudflare, Inc. All rights reserved.
# Cloudflare, Inc. Confidential and Proprietary.

# Import python stdlib

# Import third party modules

# Import Arista modules
import Cell
import BasicCli
import CliParser
import ConfigMount
import HostnameCli

from CliModel import Model

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
        print 'Will display probes config.'

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


def doDeleteProbeName( mode, probeName, options=None ):
    print 'Will delete probe {}'.format(probeName)


def doDelteProbeTestConfig( mode, probeName, testName, options=None ):
    print 'Will delete {0}, under probe {1} with options {2}'.format(
        testName,
        probeName,
        str(options)
    )

def doConfigProbeTest( mode, probeName, testName, options=None ):
    print 'Will configure test {0}, under probe {1} with options {2}'.format(
        testName,
        probeName,
        str(options)
    )

BasicCli.GlobalConfigMode.addCommand(
   ( BasicCli.noOrDefault, tokenConfigProbes, doDisableProbes ) )

BasicCli.GlobalConfigMode.addCommand(
   ( BasicCli.noOrDefault, tokenConfigProbes, tokenProbeNameKnob, tokenProbeName,
     doDeleteProbeName ) )

BasicCli.GlobalConfigMode.addCommand(
   ( [BasicCli.noOrDefault, tokenConfigProbes, tokenProbeNameKnob, tokenProbeName, tokenTestKnob, tokenTestName,
     CliParser.SetRule(
         ( '>>source', tokenTestSource, tokenSourceIpAddrOrHostname ),
         ( '>>target', tokenTarget, tokenTargetIpAddrOrHostname ),
         ( '>>count', tokenCount, countNumberRule ),
         ( '>>interval', tokenInterval, intervalNumberRule ),
         ( '>>type', tokenType, monthRule ),
         name='options' ),
     doDelteProbeTestConfig ) )

BasicCli.GlobalConfigMode.addCommand(
   ( tokenConfigProbes, tokenProbeNameKnob, tokenProbeName, tokenTestKnob, tokenTestName,
     CliParser.SetRule(
         ( '>>source', tokenTestSource, tokenSourceIpAddrOrHostname ),
         ( '>>target', tokenTarget, tokenTargetIpAddrOrHostname ),
         ( '>>count', tokenCount, countNumberRule ),
         ( '>>interval', tokenInterval, intervalNumberRule ),
         ( '>>type', tokenType, monthRule ),
         name='options' ),
     doConfigProbeTest ) )

# Plugin definition
def Plugin( entityManager ):
    pass
   # global probesConfig
   # probesConfig = ConfigMount.mount(
   #    entityManager, "probes/config", "Probes::Config", "w" )
