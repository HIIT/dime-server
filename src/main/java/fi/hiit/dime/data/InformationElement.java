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

package fi.hiit.dime.data;

import com.fasterxml.jackson.annotation.JsonIgnore;
import org.springframework.data.annotation.Transient;
import org.springframework.data.mongodb.core.index.TextIndexed;
import org.springframework.data.mongodb.core.mapping.TextScore;

/**
   Base class for all information elements, e.g. documents, messages
   etc that are involved in events.
*/
public class InformationElement extends DiMeData {
    /** URI of the information element, e.g. path on computer or web URL.
     */
    public String uri;

    /** Plain text content of the information element. This is indexed
       for text search.
    */
    @TextIndexed public String plainTextContent;

    /** Form of storage according to the Semantic Desktop ontology:
       http://www.semanticdesktop.org/ontologies/2007/03/22/nfo
     */
    public String isStoredAs;

    /** Detailed data type according to the Semantic Desktop ontology: 
	http://www.semanticdesktop.org/ontologies/2007/03/22/nfo
     */
    public String type;

    /** Relevance to text query, filled in by DiMe when returning
     * search results.
     */
    @TextScore 
    public Float score;

    @JsonIgnore
    @Transient
    public boolean isIndexed = false;

    /** Determines if this element is a stub, i.e. contains only the
        id of a previously uploaded object.

	@return True if this is a "stub" object
     */
    @JsonIgnore
    public boolean isStub() {
	return (uri == null || uri.isEmpty()) &&
	    (plainTextContent == null || plainTextContent.isEmpty());
    }
}
