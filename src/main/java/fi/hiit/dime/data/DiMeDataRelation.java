/*
  Copyright (c) 2016 University of Helsinki

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

import fi.hiit.dime.authentication.User;

import com.fasterxml.jackson.annotation.*;
import org.springframework.data.jpa.domain.AbstractPersistable;

import javax.persistence.MappedSuperclass;
import javax.persistence.Transient;

/**
   General class representing a relation to a DiMeData object.
*/
@JsonInclude(value=JsonInclude.Include.NON_NULL)
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler", "new", "data"})
@MappedSuperclass
public abstract class DiMeDataRelation<T extends DiMeData> extends AbstractPersistable<Long> {
    public DiMeDataRelation() {
    }

    /** Get the related data. 
     *  @return the data object
     */
    @Transient
    public abstract T getData();

    /** Set the related data. 
     *  @param data The data object to assign to the relation
     */
    public abstract void setData(T data);

    /** The weight of the relationship, e.g. probability of being related. */
    public Double weight;
    
    /** Application that generated the relation. */
    public String actor;

    /** Set to true if it has been explicitly valided by the user. */
    public Boolean validated;
}
