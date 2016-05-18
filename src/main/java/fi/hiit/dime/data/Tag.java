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

import java.util.Date;

import com.fasterxml.jackson.annotation.*;

import org.springframework.data.jpa.domain.AbstractPersistable;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Inheritance;
import javax.persistence.InheritanceType;

/**
   Class representing a text tag.
*/
@JsonInclude(value=JsonInclude.Include.NON_NULL)
@JsonTypeInfo(use=JsonTypeInfo.Id.NAME, include=JsonTypeInfo.As.PROPERTY, property="@type")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler", "new", "id"})
@Entity
@Inheritance(strategy=InheritanceType.SINGLE_TABLE)
@JsonSubTypes({@JsonSubTypes.Type(value = ReadingTag.class, name = "ReadingTag")})
// @Embeddable
public class Tag extends AbstractPersistable<Long> {
    public Tag() {
        this.time = new Date();
    }
    
    public Tag(String text) {
        this.text = text;
        this.time = new Date();
        this.auto = false;
        this.weight = 1.0;
    }

    public Tag(String text, boolean auto) {
        this.text = text;
        this.time = new Date();
        this.auto = auto;
        this.weight = 1.0;
    }

    /** Text of the tag. */
    @Column(columnDefinition="text")
    public String text;

    /** Time when the tag was added. */
    public Date time;

    /** Typically the host name of the computer where the event was generated.
     */
    public String origin;

    /** True if tag was automatically extracted (not via human
        interaction). 
    */
    public Boolean auto;

    /** The program that produced the event, e.g. "Firefox".
     */
    public String actor;

    /** Weight of tag between 0.0 and 1.0, higher value means more relevant. */
    public Double weight;
}
