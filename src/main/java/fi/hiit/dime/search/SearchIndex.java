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

package fi.hiit.dime.search;

import fi.hiit.dime.authentication.User;
import fi.hiit.dime.data.DiMeData;
import fi.hiit.dime.data.Event;
import fi.hiit.dime.data.InformationElement;
import fi.hiit.dime.data.ReadingEvent;
import fi.hiit.dime.data.ResourcedEvent;
import fi.hiit.dime.data.SearchEvent;
import fi.hiit.dime.database.EventDAO;
import fi.hiit.dime.database.InformationElementDAO;
import fi.hiit.dime.search.SearchQuery;
import fi.hiit.dime.search.TextSearchQuery;
import fi.hiit.dime.search.KeywordSearchQuery;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.LongField;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.Term;
import org.apache.lucene.queryparser.flexible.core.QueryNodeException;
import org.apache.lucene.queryparser.flexible.standard.StandardQueryParser;
import org.apache.lucene.search.BooleanClause;
import org.apache.lucene.search.BooleanQuery;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.MatchAllDocsQuery;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TermQuery;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.FSDirectory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
   Class that encapsulates the search index.
*/
public class SearchIndex {
    private static final Logger LOG = LoggerFactory.getLogger(SearchIndex.class);

    private static final String idField = "id";
    private static final String userIdField = "userId";
    private static final String textQueryField = "plainTextContent";
    private static final String classField = "@type";
    private static final String typeField = "type";

    private static final String versionField = "dime_version";
    private static final String currentVersion = "4";

    private static final String dataClassPrefix = "fi.hiit.dime.data.";

    private FSDirectory fsDir;
    private DirectoryReader reader = null;
    private IndexSearcher searcher = null;
    private StandardQueryParser parser;

    @Autowired
    private InformationElementDAO infoElemDAO;

    @Autowired
    private EventDAO eventDAO;

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
       Get the set of indexed object ids.
    */
    protected Set<String> indexedIds(IndexReader reader) throws IOException {
	Set<String> ids = new HashSet<String>();

	Set<String> fields = new HashSet<String>();
	fields.add(idField);
	
	for (int i=0; i<reader.maxDoc(); i++) {
	    Document doc = reader.document(i, fields);
	    String docId = doc.get(idField);
	    
	    ids.add(docId);
	}

	return ids;
    }

    /**
      Convert DiMeData object into a string to be used as the Lucene doc id.
    */
    private String luceneId(DiMeData obj) {
	if (obj instanceof Event)
	    return "event_" + obj.getId();
	else
	    return "elem_" + obj.getId();
    }

    /**
      Convert the Lucene doc id into an DiMeData object, 
    */
    private DiMeData idToObject(String docId) {
	String[] parts = docId.split("_", 2);

	if (parts.length == 2) {
	    String type = parts[0];
	    Long id = Long.parseLong(parts[1], 10);

	    if (type.equals("elem")) {
		return infoElemDAO.findById(id);
	    } else if (type.equals("event")) {
		return eventDAO.findById(id);
	    }
	}

	return null;
    }

    /**
      Convert DiMeData object into the plain text content string that
      is meant to be indexed.
    */
    private String dataContent(DiMeData obj) {
	if (obj instanceof ReadingEvent)
	    return ((ReadingEvent)obj).plainTextContent;
	else if (obj instanceof SearchEvent)
	    return ((SearchEvent)obj).query;
	else if (obj instanceof InformationElement)
	    return ((InformationElement)obj).plainTextContent;

	return null;
    }

    /**
       Return short class name for any DiMeData object.
    */
    private String getClassName(DiMeData obj) {
	String fullClassName = obj.getClass().getName();
	if (!fullClassName.startsWith(dataClassPrefix)) {
	    LOG.error("Unexpected class name {}, doesn't start with '{}'.",
		      fullClassName, dataClassPrefix);
	    return null;
	}
	return fullClassName.substring(dataClassPrefix.length());
    }

    /**
       call to update index, e.g. after adding new information elements.

       @return Number of elements that were newly indexed
    */
    public long updateIndex(boolean quickUpdate) {
	if (quickUpdate && !infoElemDAO.hasUnIndexed())
	    return 0;
	
	long count = 0;

	LOG.debug("Updating Lucene index ....");
	try {
	    boolean forceReindex = false;
	    IndexWriter writer = getIndexWriter();
	    String version = writer.getCommitData().get(versionField);

	    if (version == null || !version.equals(currentVersion)) {
		if (version != null)
		    LOG.info("Lucene index version has changed {} -> {}, " +
			     "reindexing all documents.", version, currentVersion);
		forceReindex = true;
	    }

	    long skipped = 0;
	    long inLuceneCount = -1;

	    List<DiMeData> toIndex = new ArrayList<DiMeData>();

	    if (quickUpdate) {
		// Just use our internal book keeping of new objects
		toIndex.addAll(infoElemDAO.getNotIndexed());
		toIndex.addAll(eventDAO.getNotIndexed());
	    } else {
		// Get the set of already indexed ids from Lucene
		Set<String> inLucene = indexedIds(DirectoryReader.open(writer, true));

		inLuceneCount = inLucene.size();

		// Loop over all elements in the database
		for (InformationElement elem : infoElemDAO.findAll()) {
		    // Update those which have not yet been indexed
		    if (forceReindex || !inLucene.contains(luceneId(elem)))
			toIndex.add(elem);
		}

		// Loop over all events in the database
		for (Event event : eventDAO.findAll()) {
		    // Update those which have not yet been indexed
		    if (forceReindex || !inLucene.contains(luceneId(event)))
			toIndex.add(event);
		}
	    }

	    Map<String, Long> cHist = new HashMap<String, Long>();

	    long tot = toIndex.size();
	    for (DiMeData obj : toIndex) {
		if (indexElement(writer, obj)) {
		    count += 1;

		    String cName = getClassName(obj);
		    long c = cHist.containsKey(cName) ? cHist.get(cName) : 0;
		    cHist.put(cName, c + 1);
		} else {
		    skipped += 1;
		}

		// LOG.debug("Count: {}, skipped: {}, total: {}", count, skipped, tot);
		if (obj instanceof Event)
		    eventDAO.setIndexed((Event)obj);
		if (obj instanceof InformationElement)
		    infoElemDAO.setIndexed((InformationElement)obj);
	    }

	    LOG.debug("Writing Lucene index to disk ...");

	    Map<String, String> commitData = new HashMap<String, String>();
	    commitData.put(versionField, currentVersion);
	    writer.setCommitData(commitData);
	    writer.close();

	    LOG.info("Lucene index updated: " +
		     (inLuceneCount >= 0 ? inLuceneCount + " previously indexed, " : "") + 
		     "added {} new objects, skipped {} objects with empty content.",
		     count, skipped);

	    LOG.debug("Indexed of different classes:");
	    for (Map.Entry<String, Long> entry : cHist.entrySet()) {
		LOG.debug("    {}\t {}", entry.getValue(), entry.getKey());
	    }
		     
	} catch (IOException e) {
	    LOG.error("Exception while updating search index: " + e);
	}

	return count;
    }

    /**
       Index a single data object.

       @param writer IndexWriter to use
       @param obj data object to add
       @return true if object was added
    */
    protected boolean indexElement(IndexWriter writer, DiMeData obj)
	throws IOException 
    {
	String content = dataContent(obj);

	if (content == null || content.isEmpty())
	    return false;

	String elemId = luceneId(obj);

	String className = getClassName(obj);
	if (className == null)
	    return false;

	String objType = "";
	if (obj.type != null)
	    objType = obj.type;

	Document doc = new Document(); // NOTE: Lucene Document!
	doc.add(new StringField(idField, elemId, Field.Store.YES));
	doc.add(new StringField(userIdField, obj.user.getId().toString(), Field.Store.YES));
	doc.add(new TextField(textQueryField, content, Field.Store.NO));
	doc.add(new StringField(classField, className, Field.Store.YES));
	doc.add(new StringField(typeField, objType, Field.Store.YES));

	// doc.add(new LongField("modified", lastModified, Field.Store.NO));

	writer.updateDocument(new Term(idField, elemId), doc);
	return true;
    }

    /**
       Map a list of DiMeData objects to a list of
       InformationElements, doing appropriate conversions. E.g. a
       ReadingEvent is mapped to its corresponding Document.
    */
    public static List<InformationElement>
	mapToElementList(List<DiMeData> dataList) 
    {
	List<InformationElement> elemList = new ArrayList<InformationElement>();
	Set<Long> seen = new HashSet<Long>();

	for (DiMeData data : dataList) {
	    InformationElement elem = null;
	    if (data instanceof InformationElement)
		elem = (InformationElement)data;
	    else if (data instanceof ResourcedEvent)
		elem = ((ResourcedEvent)data).targettedResource;
	    
	    if (elem != null && !seen.contains(elem.getId())) {
		elemList.add(elem);
		seen.add(elem.getId());
	    }
	}

	return elemList;
    }

    /**
       Map a list of DiMeData objects to a list of Events, doing
       appropriate conversions. E.g. a Document is mapped to its
       corresponding ReadingEvents.
    */
    public List<Event> mapToEventList(List<DiMeData> dataList, User user) {
	List<Event> events = new ArrayList<Event>();
	Set<Long> seen = new HashSet<Long>();

	for (DiMeData data : dataList) {
	    if (data instanceof InformationElement) {
		List<ResourcedEvent> expandedEvents =
		    eventDAO.findByElement((InformationElement)data, user);
		for (ResourcedEvent event : expandedEvents) {
		    event.targettedResource.plainTextContent = null;
		    event.score = event.targettedResource.score;
		    if (!seen.contains(event.getId())) {
			events.add(event);
			seen.add(event.getId());
		    }
		}
	    } else if (data instanceof Event) {
		Event event = (Event)data;
		if (!seen.contains(event.getId())) {
		    if (event instanceof ResourcedEvent)
			((ResourcedEvent)event).targettedResource.plainTextContent = null;
		    events.add(event);
		    seen.add(event.getId());
		}
	    }
	}
	return events;
    }


    /**
       Perform text search to Lucene index.

       @param query Query string
       @param limit Maximum number of results to return
       @param userId DiMe user id.
    */
    public List<DiMeData> search(SearchQuery query, String className,
				 String typeName, int limit, Long userId)
	throws IOException
    {
	if (limit < 0)
	    limit = 100;

	List<DiMeData> objs = new ArrayList<DiMeData>();

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

	    Query textQuery = null;
	
	    if (query instanceof TextSearchQuery) {
		textQuery = basicTextQuery(((TextSearchQuery)query).query);
	    } else if (query instanceof KeywordSearchQuery) {
		textQuery = keywordSearchQuery(((KeywordSearchQuery)query).
					       weightedKeywords);
	    } else {
		textQuery = new MatchAllDocsQuery();
	    }
	    queryBuilder.add(textQuery, BooleanClause.Occur.MUST);

	    queryBuilder.add(new TermQuery(new Term(userIdField, 
						    userId.toString())),
			     BooleanClause.Occur.FILTER);

	    if (className != null)
		queryBuilder.add(new TermQuery(new Term(classField, className)), 
				 BooleanClause.Occur.FILTER);

	    if (typeName != null)
		queryBuilder.add(new TermQuery(new Term(typeField, typeName)),
				 BooleanClause.Occur.FILTER);

	    TopDocs results = searcher.search(queryBuilder.build(), limit);
	    ScoreDoc[] hits = results.scoreDocs;

	    for (int i=0; i<hits.length; i++) {
		Document doc = searcher.doc(hits[i].doc);
		float score = hits[i].score;
		String docId = doc.get(idField);
		try {
		    DiMeData obj = idToObject(docId);
		    if (obj == null) {
			LOG.error("Bad doc id: "+ docId);
		    } else if (obj.user.getId().equals(userId)) {
			obj.score = score;
			objs.add(obj);
		    } else {
			LOG.warn("Lucene returned result for wrong user: " +
				 obj.getId());
		    }
		} catch (NumberFormatException ex) {
		    LOG.error("Lucene returned invalid id: {}", docId);
		}
	
	    }
	} catch (QueryNodeException e) {
	     LOG.error("Exception: " + e);
	}	 
	return objs;
    }

    protected Query basicTextQuery(String query) throws QueryNodeException {
	return this.parser.parse(query, textQueryField);
    }

    protected Query keywordSearchQuery(List<WeightedKeyword> weightedKeywords) {
	// Andrej: remove the line below, and add your code here

	return new MatchAllDocsQuery();
    }

}
