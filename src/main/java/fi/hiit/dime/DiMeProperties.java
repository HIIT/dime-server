/*
  Copyright (c) 2015 University of Helsinki

  Permission is hereby granted, free of charge, to any person
  obtaining a copy of this software and associated documentation files
  (the "Software"), to deal in the Software without restriction,
  including without limitation the rights to use, copy, modify, merge,
  publish, distribute, sublicense, and/or sell copies of the Software,
  and to permit persons to whom the Software is furnished to do so,
  subject to the following conditions:

  The above copyright notice and this permission notice shall be
  included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
  ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
*/

package fi.hiit.dime;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@ConfigurationProperties(ignoreUnknownFields = false, 
                         prefix = "dime")
@Component
public class DiMeProperties {
    private String luceneIndexPath;
    public void setLuceneIndexPath(String s) { luceneIndexPath = s; }
    public String getLuceneIndexPath() { return luceneIndexPath; }

    private String luceneAnalyzer = "Standard";
    public void setLuceneAnalyzer(String s) { 
        luceneAnalyzer = s; //.replaceAll("Analyzer$", "");
    }
    public String getLuceneAnalyzer() { return luceneAnalyzer; }

    private String[] corsAllowOrigin = null;
    public void setCorsAllowOrigin(String[] s) { corsAllowOrigin = s; }
    public String[] getCorsAllowOrigin() { return corsAllowOrigin; }

    private String leaderboardEndpoint = "https://dimeproxy.hiit.fi/dime-leaderboards/api/event";
    public void setLeaderboardEndpoint(String s) { leaderboardEndpoint = s; }
    public String getLeaderboardEndpoint() { return leaderboardEndpoint; }

    private String peoplefinderEndpoint = "https://peoplefinder.danubetech.com/xdi/graph";
    public void setPeoplefinderEndpoint(String s) { peoplefinderEndpoint = s; }
    public String getPeoplefinderEndpoint() { return peoplefinderEndpoint; }

    private String baseUri = "http://localhost:8080/";
    public void setBaseUri(String s) { baseUri = s; }
    public String getBaseUri() { return baseUri; }
}
