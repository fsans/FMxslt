FMxslt
======

FileMaker XSLT replacement API

@author Francesc Sans fsans@ntwk.es
@version 0.1 **(Alpha release)**
 
Copyright (c) 2012 Network BCN Software
 
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

 ------------------------------------------------------------------------------

 **FileMaker XSLT API replacement CGI**

Transparently replaces FileMaker pre v12 XSLT API
  
Use the same XSLT stylesheets designed for FileMaker XSLT API without changes. 
 
Fill the config.xml file (open the default file provided to see details). 
 
To setup the replacement in FM12 and later, do one of the follwing options: 
<<<<<<< HEAD

	A. Add  the key=value pair "adapter=your_stilesheet_file.xsl" to the usual query string used before.
	B. Setup a redirect in the HTTP server from "/fmi/xsl/ to the gateway /fm.cgi. This will catch all your old xslt queries and pass it to the new CGI.
	
=======
 
	A. Add  the key=value pair "adapter=adapter_filer.xsl" to the usual query string used before.
	B. Setup a redirect in the HTTP server from "/fmi/xsl/ to the gateway /fm.cgi. This will catch all your old xslt queries and pass it to the new CGI. 
 
>>>>>>> minor updates
Accepts POST, GET or HEAD http requests 

 ------------------------------------------------------------------------------

NOTE: This is an ALPHA release, proof of concept, software. Currently in active development. Send me suggestions if you're interested.


