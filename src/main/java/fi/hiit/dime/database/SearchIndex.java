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

package fi.hiit.dime.database;

import fi.hiit.dime.data.InformationElement;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.Term;
import org.apache.lucene.store.FSDirectory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;

import java.nio.file.Paths;
import java.io.IOException;
import java.util.List;

/**
   Class that encapsulates the search index.
*/
public class SearchIndex {
    private static final Logger LOG = LoggerFactory.getLogger(SearchIndex.class);

    private IndexWriterConfig iwc;
    private FSDirectory fsDir;

    @Autowired
    private InformationElementDAO infoElemDAO;

    /**
       Constructor.
       
       @param indexPath Path to Lucene index
    */
    public SearchIndex(String indexPath) throws IOException {
	fsDir = FSDirectory.open(Paths.get(indexPath));

        iwc = new IndexWriterConfig(new StandardAnalyzer());
        iwc.setOpenMode(OpenMode.CREATE_OR_APPEND);

    	// Advice from Lucene example:
    	// http://lucene.apache.org/core/5_3_0/demo/src-html/org/apache/lucene/demo/IndexFiles.html
    	// Optional: for better indexing performance, if you
    	// are indexing many documents, increase the RAM
    	// buffer.  But if you do this, increase the max heap
    	// size to the JVM (eg add -Xmx512m or -Xmx1g):
    	//
    	// iwc.setRAMBufferSizeMB(256.0);
    }

    /**
       Get an IndexWriter for writing to the index. Remember to close
       after use!

       @return An IndexWriter instance
    */
    protected IndexWriter getIndexWriter() throws IOException {
	IndexWriter writer = new IndexWriter(fsDir, iwc);

    	// NOTE: if you want to maximize search performance,
    	// you can optionally call forceMerge here.  This can be
    	// a terribly costly operation, so generally it's only
    	// worth it when your index is relatively static (ie
    	// you're done adding documents to it):
    	//
    	// writer.forceMerge(1);

	return writer;
    }

    /**
       Call to update index, e.g. after adding new information elements.

       @return Number of elements that were newly indexed
    */
    public long updateIndex() {
	long count = infoElemDAO.countNotIndexed();
	
	if (count > 0) {
	    LOG.info("Found " + count + " information elements not yet indexed. " +
		     "Proceeding to update index ...");

	    try {
		IndexWriter writer = getIndexWriter();	

		for (InformationElement elem : infoElemDAO.findNotIndexed()) {
		    indexElement(writer, elem);
		}

		writer.close();
	    } catch (IOException e) {
		LOG.error("Exception while updating search index: " + e);
	    }
	}
	return count;
    }

    /**
       Index a single information element.

       @param writer IndexWriter to use
       @param elem InformationElement to add
       @return true if element was added
    */
    protected boolean indexElement(IndexWriter writer, InformationElement elem)
	throws IOException 
    {
	if (elem.plainTextContent == null || elem.plainTextContent.isEmpty()) {
	    LOG.warn("Not indexing empty plainTextContent: " + elem.id);
	    return false;
	}

	LOG.info("Indexing document " + elem.id);

	Document doc = new Document(); // NOTE: Lucene Document!

	Field idField = new StringField("id", elem.id, Field.Store.YES);
	doc.add(idField);

	// doc.add(new LongField("modified", lastModified, Field.Store.NO));

	doc.add(new TextField("plainTextContent", elem.plainTextContent,
			      Field.Store.NO));

	writer.updateDocument(new Term("id", elem.id), doc);
	return true;
    }
}
