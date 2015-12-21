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

import java.util.HashSet;
import java.util.Set;

import javax.persistence.Column;
import javax.persistence.ElementCollection;
import javax.persistence.Entity;
import javax.persistence.FetchType;
import javax.persistence.Inheritance;
import javax.persistence.InheritanceType;
import javax.persistence.JoinColumn;

/**
   Base class for all information elements, e.g. documents, messages
   etc that are involved in events.
*/
@Entity
@Inheritance(strategy=InheritanceType.SINGLE_TABLE)
public class InformationElement extends DiMeData {
    public static InformationElement makeStub(Long id) {
	InformationElement elem = new InformationElement();
	elem.setId(id);
	return elem;
    }

    public static InformationElement makeStub(InformationElement e) {
	return makeStub(e.getId());
    }

    /** URI of the information element, e.g. path on computer or web URL.
     */
    @Column(columnDefinition="text")
    public String uri;

    /** Plain text content of the information element. This is indexed
       for text search.
    */
    @Column(columnDefinition="longtext")
    public String plainTextContent;

    /** Form of storage according to the Semantic Desktop ontology:
       http://www.semanticdesktop.org/ontologies/2007/03/22/nfo
     */
    public String isStoredAs;

    /** Determines if this element is a stub, i.e. contains only the
        id of a previously uploaded object.

	@return True if this is a "stub" object
     */
    @JsonIgnore
    public boolean isStub() {
	return (uri == null || uri.isEmpty()) &&
	    (plainTextContent == null || plainTextContent.isEmpty());
    }

    /** List of user-specified tags, interpretation depends on the
	application. 
    */
    @ElementCollection(targetClass = String.class)
    public Set<String> tags;

    /** String value to uniquely identify an object. */
    public String contentHash;

    /** Add a free-form tag to the object.
	@param tag The tag to add
    */
    public void addTag(String tag) {
	if (tags == null)
	    tags = new HashSet<String>();
	tags.add(tag);
    }

    /** Remove a tag from the object.
	@param tag The tag to remove
    */
    public void removeTag(String tag) {
	if (tags != null)
	    tags.remove(tag);
    }

    /** Checks if the object contains a given tag.
	@param tag Tag to check for
	@return true if tag found, otherwise false
    */
    public boolean hasTag(String tag) {
	return tags != null && tags.contains(tag);
    }

    /** Method to call when ever a new object has been uploaded, e.g.
	to clean up user provided data, or perform some house keeping
	before storing in the database.
    */
    @Override
    public void autoFill() {} 
}
