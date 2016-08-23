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
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler", "new"})
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

    public Tag(String text, boolean auto, String actor) {
        this.text = text;
        this.time = new Date();
        this.auto = auto;
        this.weight = 1.0;
        this.actor = actor;
    }

    public Tag(String text, String actor) {
        this.text = text;
        this.time = new Date();
        this.auto = false;
        this.weight = 1.0;
        this.actor = actor;
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

    /** Tests tag equality, i.e. if the text and actor fields are identical.

        @param that the tag to test with
        @return True if the tags are equal.
    */
    public boolean tagEquals(Tag that) {
        // First check if texts equal
        if (!this.text.equals(that.text))
            return false;

        // If this actor is null, both have to be null
        if (this.actor == null)
            return that.actor == null;

        // Otherwise, check that actors equal
        return this.actor.equals(that.actor);
    }

    /** Tests if a given tag matches the given template tag one. A
        matching tag is one that has identical tag text and the same
        actor.

        If the actor is null in the template, this is interpreted as a
        wild card field, i.e. any value of actor is matched (including
        null).

        @param template Tag template to match with
        @return True if the given tag matches this one
    */
    public boolean matches(Tag template) {
        // If texts don't match, we can give up already
        if (!this.text.equals(template.text))
            return false;

        // If template actor is non-null, test if they match
        if (template.actor != null)
            return template.actor.equals(this.actor);
        
        // Otherwise, any value is acceptable (as we've already
        // established that the texts match)
        return true;
    }

}
