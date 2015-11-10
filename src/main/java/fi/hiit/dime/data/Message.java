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

import java.util.Date;
import java.util.List;

import javax.persistence.CascadeType;
import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.JoinColumn;
import javax.persistence.JoinTable;
import javax.persistence.ManyToOne;
import javax.persistence.OneToMany;
import javax.persistence.ManyToMany;

/**
   Class representing an electronic message, such as an email.
*/
@Entity
public class Message extends InformationElement {
    public Date date;
    
    @Column(columnDefinition="text")
    public String subject;

    @Column(columnDefinition="text")
    public String fromString;

    @ManyToOne(cascade=CascadeType.ALL)
    @JoinColumn(name="from_id")
    public Person from;

    @Column(columnDefinition="text")
    public String toString;

    @ManyToMany(cascade=CascadeType.ALL)
    @JoinTable(name="message_to", 
	       joinColumns={@JoinColumn(name="message_id", referencedColumnName="id")},
	       inverseJoinColumns={@JoinColumn(name="person_id", referencedColumnName="id")})
    public List<Person> to;

    @Column(columnDefinition="text")
    public String ccString;

    @ManyToMany(cascade=CascadeType.ALL)
    @JoinTable(name="message_cc", 
	       joinColumns={@JoinColumn(name="message_id", referencedColumnName="id")},
	       inverseJoinColumns={@JoinColumn(name="person_id", referencedColumnName="id")})
    public List<Person> cc;

    @OneToMany
    public List<InformationElement> attachments;
    
    @Column(columnDefinition="text")
    public String rawMessage;

    @Override
    public void autoFill() {
	if (subject != null && subject.length() > 0 && 
	    !plainTextContent.startsWith(subject))
	    plainTextContent = subject + "\n\n" + plainTextContent;
    }
}
