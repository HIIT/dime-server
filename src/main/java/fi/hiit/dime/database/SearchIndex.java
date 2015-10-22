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
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.Term;
import org.apache.lucene.queryparser.flexible.standard.StandardQueryParser;
import org.apache.lucene.queryparser.flexible.core.QueryNodeException;
import org.apache.lucene.search.BooleanClause;
import org.apache.lucene.search.BooleanQuery;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TermQuery;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.FSDirectory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;

import java.nio.file.Paths;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
   Class that encapsulates the search index.
*/
public class SearchIndex {
    private static final Logger LOG = LoggerFactory.getLogger(SearchIndex.class);

    private static final String idField = "id";
    private static final String userIdField = "userId";
    private static final String textQueryField = "plainTextContent";

    private FSDirectory fsDir;

    private DirectoryReader reader = null;
    private IndexSearcher searcher;
    private StandardQueryParser parser;

    @Autowired
    private InformationElementDAO infoElemDAO;

    /**
       Constructor.
       
       @param indexPath Path to Lucene index
    */
    public SearchIndex(String indexPath) throws IOException {
	fsDir = FSDirectory.open(Paths.get(indexPath));

	// FIXME: check if index was destroyed, i.e. would need
	// reindexing

	parser = new StandardQueryParser(new StandardAnalyzer());
    }

    /**
       Get an IndexWriter for writing to the index. Remember to close
       after use!

       @return An IndexWriter instance
    */
    protected IndexWriter getIndexWriter() throws IOException {
	IndexWriterConfig iwc = new IndexWriterConfig(new StandardAnalyzer());
        iwc.setOpenMode(OpenMode.CREATE_OR_APPEND);

    	// Advice from Lucene example:
    	// http://lucene.apache.org/core/5_3_0/demo/src-html/org/apache/lucene/demo/IndexFiles.html
    	// Optional: for better indexing performance, if you
    	// are indexing many documents, increase the RAM
    	// buffer.  But if you do this, increase the max heap
    	// size to the JVM (eg add -Xmx512m or -Xmx1g):
    	//
    	// iwc.setRAMBufferSizeMB(256.0);

	IndexWriter writer = new IndexWriter(fsDir, iwc);

    	// NOTE: if you want to maximize search performance,
    	// you can optionally call forceMerge here.  This can be
    	// a terribly costly operation, so generally it's only
    	// worth it when your index is relatively static (ie
    	// you're done adding documents to it):
    	//
    	// writer.forceMerge(1);

	// Also, for low-latency turnaround it's best to use a
	// near-real-time reader
	// (DirectoryReader.open(IndexWriter,boolean)). Once you have
	// a new IndexReader, it's relatively cheap to create a new
	// IndexSearcher from it.

	return writer;
    }

    /**
       Call to update index, e.g. after adding new information elements.

       @return Number of elements that were newly indexed
    */
    public long updateIndex(boolean forceAll) {
	long count = 0;

	if (forceAll || infoElemDAO.countNotIndexed() > 0) {
	    LOG.info("Updating Lucene index .... {}", forceAll);
	    try {
		IndexWriter writer = getIndexWriter();
		int skipped = 0;

		Iterable<InformationElement> toIndex;
		if (forceAll) 
		    toIndex = infoElemDAO.findAll();
		else
		    toIndex = infoElemDAO.findNotIndexed();

		for (InformationElement elem : toIndex) {
		    System.out.println("ELEM");
		    if (!indexElement(writer, elem))
			skipped += 1;
		}

		writer.close();

		for (InformationElement elem : toIndex) {
		    // NOTE: we are also marking those which were
		    // skipped as "isIndexed" since otherwise DiMe
		    // would repeatedly try to index them again...

		    elem.isIndexed = true;
		    infoElemDAO.save(elem);
		    count += 1;
		}

		LOG.info("Indexed {} information elements.", count);
		if (skipped > 0)
		    LOG.info("Skipped {} elements with empty content.", skipped);

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
	if (elem.plainTextContent == null || elem.plainTextContent.isEmpty())
	    return false;

	LOG.debug("Indexing document {}", elem.getId());

	Document doc = new Document(); // NOTE: Lucene Document!

	doc.add(new StringField(idField, elem.getId(), Field.Store.YES));

	doc.add(new StringField(userIdField, elem.user.getId(), Field.Store.YES));

	doc.add(new TextField(textQueryField, elem.plainTextContent,
			      Field.Store.NO));

	// doc.add(new LongField("modified", lastModified, Field.Store.NO));

	writer.updateDocument(new Term(idField, elem.getId()), doc);
	return true;
    }

    /**
       Perform text search to Lucene index.

       @param query Query string
       @param limit Maximum number of results to return
       @param userId DiMe user id.
    */
    public List<InformationElement> textSearch(String query, int limit,
					       String userId)
	throws IOException
    {
	if (limit < 0)
	    limit = 100;

	List<InformationElement> elems = new ArrayList<InformationElement>();

	try {
	    if (reader == null) {
		reader = DirectoryReader.open(fsDir);
		searcher = new IndexSearcher(reader);
	    }

	    DirectoryReader newReader = DirectoryReader.openIfChanged(reader);

	    // Reinitialise reader and searcher if the index has changed.
	    if (newReader != null) {
		reader.close();
		reader = newReader;
		searcher = new IndexSearcher(reader);
	    }

	    BooleanQuery.Builder queryBuilder = new BooleanQuery.Builder();

	    Query textQuery = parser.parse(query, textQueryField);
	    queryBuilder.add(textQuery, BooleanClause.Occur.MUST);

	    Query userQuery = new TermQuery(new Term(userIdField, userId));
	    queryBuilder.add(userQuery, BooleanClause.Occur.FILTER);

	    TopDocs results = searcher.search(queryBuilder.build(), limit);
	    ScoreDoc[] hits = results.scoreDocs;

	    for (int i=0; i<hits.length; i++) {
		Document doc = searcher.doc(hits[i].doc);
		float score = hits[i].score;
		String docId = doc.get(idField);
		
		InformationElement elem = infoElemDAO.findById(docId);
		if (elem == null) 
		    LOG.error("Bad doc id: "+ docId);
		else if (elem.user.getId().equals(userId))
		    elems.add(elem);
		else
		    LOG.warn("Lucene returned result for wrong user: " + elem.getId());
	    }
	} catch (QueryNodeException e) {
	     LOG.error("Exception: " + e);
	}	 
	return elems;
    }
}
