#!/opt/local/bin/perl
#
#  
#  @author Francesc Sans fsans@ntwk.es
#  @version 0.1
#  
#  Copyright (c) 2012 Network BCN Software
#  
#  his program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
##------------------------------------------------------------------------------
# FileMaker XSLT API replacement CGI
# Transparently replace FileMaker pre v12 XSLT API
# 
# Use the same XSLT stylesheets designed for FileMaker XSLT API without changes
# To setup the replacement in FM12 and later, do one of the follwing options:
#	A. Add "adapter=your_stilesheet_file.xsl" to the usual query string used before
#	B. Setup a redirect in the HTTP server to the gateway fm.cgi
#	
#	Accept POST, GET, HEAD
#	
##------------------------------------------------------------------------------
# $ Revision: 0.1.026 $ - $Author: Francesc Sans fsans@ntwk.es $ - $Date: 2012/01/01 00:00:00 $
##------------------------------------------------------------------------------
#
#
#
use XML::Simple;
use XML::LibXSLT;
use XML::LibXML;
use File::Path;
use Data::Dumper;
use XML::Parser;
use HTTP::Request::Common qw(POST);
use LWP::UserAgent;

use strict;
use warnings;

#! Always use full paths if this script has to be launched from launchd or cron
use File::Basename;
my $rootdirectory = dirname(__FILE__)."/";


#! #####################################################
#! parse config.xml

my $xml = new XML::Simple;
my $data = $xml->XMLin($rootdirectory."config.xml");

#! service parameters
my $protocol = $data->{protocol};
my $host = $data->{host};
my $fmcgi = $data->{fmcgi};
my $user = $data->{user};
my $password = $data->{password};
my $port = $data->{port};
my $database = $data->{database};
my $debug = $data->{debug};



#! #####################################################
#! 
#! complete URI resource to FileMaker FMRESULTSET gateway
my $endpoint = $protocol . $host . ":" . $port . "/" . $fmcgi;

#! array of name=value pairs 
my @qarray; 


#! #####################################################
#! array of tokens to inhject as parameters to the adapter
my %Tokens;

my %EmbededParams;

# fmp namespace definition
my $fmqNamespace = "http://www.filemaker.com/xml/query";
my $fmqNamespaceAlias = "fmq";

# create the request-query object
my $requestQueryObject = XML::LibXML::Document->new( '1.0', 'UTF-8' );

my $queryObjectBody = $requestQueryObject->createElement( 'query' );
$requestQueryObject->setDocumentElement( $queryObjectBody );
$queryObjectBody->setNamespace( $fmqNamespace , $fmqNamespaceAlias, 0 );
# to add more namespaces: (1 adds alias)
# $queryObjectBody->setNamespace( 'http://www.w3.org/bla' , 'bla', 1 );


#! post query string values
my $qstring;


#! #####################################################
# setup headers
print "content-type:text/xml;charset=utf-8\n\n" ;




#! #####################################################
#! params:
#! uri -> endpoint url
#! query -> name value pairs string
#
sub getDataFromDatabase
{
	my ($ua,$req);
	my $uri  = $_[0];
	my $query = $_[1];
	
	#&print_log("uri: $uri\n");
	#&print_log("query: $query\n");
	
	$ua = LWP::UserAgent->new();
	$req = HTTP::Request->new(POST => $uri);
	
	#! add query string (name value pairs)
	$req->content_type('application/x-www-form-urlencoded');
	$req->content($query);
	
	return 	$ua->request($req)->as_string;
	
}


#! #####################################################
#! params:
#! sourceFile -> file to read
#! returs readed file stream
#
sub readAdapter
{
	
	my $sourceData;
	my $sourceFile  = $_[0];
	
	open FILE, $rootdirectory.$sourceFile or die "Couldn't open file: $!"; 
	while (<FILE>){
	 $sourceData .= $_;
	}
	
	return 	$sourceData;
}


#! #####################################################

#! Read all CGI vars into an associative array.
sub getcgivars 
{
    my ($QueryString,@NameValuePairs,%Vars);

    #! read entire string of CGI vars into $in
	#! Whether the method used is GET or POST, store the parameters passed in $QueryString
	if($ENV{'REQUEST_METHOD'} eq "POST") {
	  read(STDIN, $QueryString, $ENV{'CONTENT_LENGTH'});
	} elsif ( ( $ENV{'REQUEST_METHOD'} eq 'GET' ) || ( $ENV{'REQUEST_METHOD'} eq 'HEAD') ) {
	  #$type = "display_form";
	  $QueryString = $ENV{QUERY_STRING};
	}else{
		 &HTMLdie("Script was called with unsupported REQUEST_METHOD.") ;
	}
	
	@NameValuePairs = split (/&/, $QueryString);
	
	#! Split each NameValue pair, replace +'s by spaces, 
	#! get the character equivalent of any data in hex (%XX) and finally, 
	#! store it in an associative array

	my ($NameValue,$Name,$Value);
	
	foreach $NameValue (@NameValuePairs) {
		($Name, $Value) = split (/=/, $NameValue);
		if($Value){
			$Value =~ tr/+/ /;
			$Value =~ s/%([\dA-Fa-f][\dA-Fa-f])/ pack ("C",hex ($1))/eg;
		}
		#! add new name value pair to the hash
		$Vars{$Name} = $Value;
	}

    return %Vars ;
}

#! #####################################################

sub buildQueryString 
{
	my ($str,@array,$val);
	my %vars  = @_;
	
	foreach (keys %vars) 
	{
		#! enable empty values (as needed for the command variables)
		$val = $vars{$_} ? $vars{$_} : "" ;
		$str = "";
	    $str .= "$_=" . $val;
		push (@array, $str);
	}

	##return @array;
	return join("&",@array);
}
#! #####################################################
#! Die, outputting HTML error page
#! If no $title, use a default title

sub HTMLdie 
{
	my ($msg,$title)= @_ ;
    $title= "CGI Error" if $title eq '' ;
    print <<EOF ;
Content-type: text/html

<html>
<head>
<title>$title</title>
</head>
<body>
<h1>$title</h1>
<h3>$msg</h3>
</body>
</html>
EOF

    exit ;
}


#! #####################################################

sub print_log()
{
	if ($debug > 0){
		print $_[0]."\n";
	}
}


#! #####################################################

#! Right-trim function to remove trailing whitespace
sub rtrim($)
{
	my $string = shift;
	$string =~ s/\s+$//;
	return $string;
}

##

#! #####################################################

##print "Content-type: text/xml\n\n" ;

#! get the CGI variables into a list of strings
my %cgivars = &getcgivars;


#! #####################################################
#! extract tokens & inject in the request-query object

my $tokenPrefix = "-token.";
my ($param,$tokenName,$tokenValue);
foreach (keys %cgivars)
{
	$tokenName = $_;
	$tokenValue = $cgivars{$_};
	
	
	if (index ($tokenName, $tokenPrefix) == 0){ #!  key starts with tokenPrefix
		
		#| add to tokens hash
		$Tokens{$tokenName} = $tokenValue;
		
		#&print_log("token: $tokenName = $tokenValue");
		
		#| remove from cgivars hash
		delete $cgivars{$tokenName};
		
		
		#!  ADD TOKENS TO request-query param objet (to be passed to the xslt later)
		#<xsl:param name="request-query" />
		# ... <xsl:value-of select="$request-query/fmq:query/fmq:parameter[@name='-token.xyz']"/>
		
		$param = $requestQueryObject->createElement('param');
		$param->setAttribute( 'name', $tokenName);
		$param->appendTextNode($tokenValue);
		$queryObjectBody->appendChild($param);
		
		#&print_log($param->toString(1));
		
	}
	
}

#&print_log("#####################################################");
#&print_log($requestQueryObject->toString(1));


#| #####################################################
#| read the XSLT file

my $adapterName = $cgivars{'adapter'};
#&print_log("adapter: $adapterName");

#! remove the adapter from the hash
delete $cgivars{'adapter'};


my $xp = new XML::Parser();
$xp->setHandlers(Proc => \&pih);
$xp->parsefile($adapterName);

my $xmldata = $xml->XMLin($adapterName);

#&print_log(Dumper($data));

#! extract process instructions and add to the qarray
sub pih() {
	# extract data 
	my($paramData,@pairs,$pName, $pValue);
	my ($PIparser, $PItarget, $PIdata) = @_;

	if (lc($PItarget) eq "xslt-cwp-query") 
	{ 
		$paramData = substr ($PIdata,index($PIdata,"=")+1 );
		#remove surrounding quotes
		$paramData =~ tr/"//d;
		#&print_log( "CWP-QUERY: " . $paramData );
		
		@pairs = split(/&/,$paramData);

		foreach my $v (@pairs) {
			($pName, $pValue) = split (/=/, $v);
			
			#! add new name value pair to the hash
			$EmbededParams{$pName} = $pValue;
			
			#&print_log( $pName. " -> " .  $pValue );
			
			#| add to tokens hash
			$cgivars{$pName} = $pValue;
		}	
	} 
}


#! #####################################################
#! concatenate name value pairs into a string

$qstring = &buildQueryString(%cgivars);
#&print_log( $qstring );



#! #####################################################
# load xml from database query
my $parser = XML::LibXML->new();
my $xmlsource = $parser->load_xml( location => $endpoint.'?'.$qstring );
#&print_log($xmlsource->toString());



# load xslt stylesheet & parse it
my $style_doc = $parser->parse_file( $adapterName );

#&print_log($style_doc->toString());

my $xslt = XML::LibXSLT->new();
my $stylesheet = $xslt->parse_stylesheet($style_doc);

&print_log($stylesheet->toString());

# inject stylesheet parameters
# (set up the request-query object)

# ###### method 2: edit the 'request-query' prebuilt parameter, add child nodes...

# select <xsl:param name="request-query" />
my $targetNode = $style_doc->findnodes('*/param/@name="request-query"');

&print_log($targetNode);

my $queryNode = $style_doc->createElement( 'query' );

$style_doc->setDocumentElement( $queryNode );

$queryNode->setNamespace( $fmqNamespace , $fmqNamespaceAlias, 0 );

$targetNode->appendChild($queryNode);


#&print_log($style_doc->toString());





# transform
#my $results = $stylesheet->transform($xmlsource,@stylesheetParams);
my $results = $stylesheet->transform($xmlsource);


#&print_log($results->toString());

#print $results->toString();


;


