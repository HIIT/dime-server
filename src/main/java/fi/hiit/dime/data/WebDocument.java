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

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

import javax.persistence.Column;
import javax.persistence.ElementCollection;
import javax.persistence.Embedded;
import javax.persistence.Entity;

@Entity
public class WebDocument extends Document {
    @ElementCollection(targetClass = String.class)
    public List<String> frequentTerms;

    @JsonProperty("abstract")
    public String abstractText;

    @Column(columnDefinition="longtext")
    public String html;

    @ElementCollection(targetClass = HyperLink.class)
    public List<HyperLink> imgURLs;
    
    @ElementCollection(targetClass = HyperLink.class)
    public List<HyperLink> hyperLinks;

    @Embedded
    public OpenGraphProtocol openGraphProtocol;

    @ElementCollection(targetClass = HtmlMetaTag.class)
    public List<HtmlMetaTag> metaTags;
}
