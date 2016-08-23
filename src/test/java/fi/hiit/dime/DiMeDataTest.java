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

package fi.hiit.dime;

import fi.hiit.dime.data.Document;
import fi.hiit.dime.data.Tag;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.boot.test.SpringApplicationConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import static org.junit.Assert.*;

import java.util.List;

/**
 * @author Mats Sjöberg (mats.sjoberg@helsinki.fi)
 */
@SpringApplicationConfiguration(classes = Application.class)
@RunWith(SpringJUnit4ClassRunner.class)
public class DiMeDataTest {
    @Test
    public void testTags() throws Exception {
        Document doc1 = new Document();
        doc1.uri = "http://www.example.com/hello.txt";
        doc1.plainTextContent = "Hello, world";
        doc1.mimeType = "text/plain";

        assertFalse(doc1.hasTags());

        doc1.addTag(new Tag("foo"));
        doc1.addTag(new Tag("foo", true));

        doc1.addTag(new Tag("foo", "actor1"));
        doc1.addTag(new Tag("foo", true, "actor1"));

        assertTrue(doc1.hasTags());
        assertTrue(doc1.hasMatchingTag("foo"));
        assertTrue(doc1.hasMatchingTag(new Tag("foo", false, "actor1")));
        assertFalse(doc1.hasMatchingTag(new Tag("foo", "actor2")));

        Tag tag1 = doc1.getTag(new Tag("foo"));
        assertEquals(null, tag1.actor);
        assertTrue(tag1.auto);

        List<Tag> matchingTags = doc1.getMatchingTags(new Tag("foo"));
        assertEquals(2, matchingTags.size());
        assertEquals(null, matchingTags.get(0).actor);
        assertEquals("actor1", matchingTags.get(1).actor);
        assertTrue(matchingTags.get(0).auto);
        assertTrue(matchingTags.get(1).auto);

        List<Tag> matchingTagsWithActor = 
            doc1.getMatchingTags(new Tag("foo", "actor1"));
        assertEquals(1, matchingTagsWithActor.size());
        assertEquals("actor1", matchingTagsWithActor.get(0).actor);
        assertTrue(matchingTagsWithActor.get(0).auto);

        List<Tag> noMatchingTags = 
            doc1.getMatchingTags(new Tag("foo", "actor2"));
        assertEquals(0, noMatchingTags.size());
        
        // Document doc2 = new Document();
        // doc2.uri = "http://www.example.com/hello2.txt";
        // doc2.plainTextContent = "Hello, world too";
        // doc2.mimeType = "text/plain";

        int removedNoneCount = doc1.removeMatchingTags(new Tag("foo", "actor2"));
        assertEquals(0, removedNoneCount);
        assertEquals(2, doc1.tags.size());

        int removedAllCount = doc1.removeMatchingTags(new Tag("foo"));
        assertEquals(2, removedAllCount);
        assertEquals(0, doc1.tags.size());
    }
}
