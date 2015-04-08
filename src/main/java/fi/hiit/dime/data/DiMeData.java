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

import org.springframework.data.annotation.Id;
import java.util.Date;

/**
   Base class for all DiMe data objects, i.e. data items uploaded to be stored.
*/
public class DiMeData {

    /** Unique identifier in the database */
    @Id
    public String id;

    /** Date and time when the object was first uploaded via the
	external API. 
     */
    public Date time_created;

    /** Date and time when the objects was last modified via the
	external API.
    */
    public Date time_modified;

    /** Type of data object.
	FIXME defined DiMe ontology for interpretation.
     */
    public String interpretation;

    /** How the data object was created.
	FIXME defined DiMe ontology for manifestation.
     */
    public String manifestation;

    /** User associated with the object. */
    public User user;

    public DiMeData() {
	// Set to current date and time
	time_created = new Date();
	time_modified = new Date();
    }	
}
