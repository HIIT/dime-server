/*
  Copyright (c) 2015-2016 University of Helsinki

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

package fi.hiit.dime.search;

import fi.hiit.dime.authentication.User;
import fi.hiit.dime.data.DiMeData;

import com.fasterxml.jackson.annotation.JsonInclude;

import java.util.ArrayList;
import java.util.List;

/** Class for containing search results and metadata. Similar to JSON
    "response" part of Solr.
*/
@JsonInclude(value=JsonInclude.Include.NON_NULL)
public class SearchResults {
    private long numFound;

    private List<DiMeData> docs;

    public List<WeightedKeyword> queryTerms;

    public String message;

    public SearchResults() {
        this.docs = new ArrayList<DiMeData>();
    }

    public SearchResults(String message) {
        this.docs = new ArrayList<DiMeData>();
        this.message = message;
    }

    /** Add a single DiMeData object to the results. 
     */
    public long add(DiMeData obj) {
        docs.add(obj);
        numFound = docs.size();
        return numFound;
    }

    /** Get the list of results.
     */
    public List<DiMeData> getDocs() { return docs; }

    /** Set the list of results to given list of DiMeData objects.
     */
    public void setDocs(List<DiMeData> docs) {
        this.docs = docs;
        numFound = docs.size();
    }

    /** Get number of results.
     */
    public long getNumFound() { return numFound; }
}
