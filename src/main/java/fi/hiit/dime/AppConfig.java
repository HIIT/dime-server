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

package fi.hiit.dime;

import com.mongodb.Mongo;
import com.mongodb.MongoClient;
import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexNotFoundException;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.flexible.standard.StandardQueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.DependsOn;
import org.springframework.data.mongodb.core.MongoTemplate;

import java.nio.file.Paths;
import java.io.IOException;

@Configuration
public class AppConfig {
    private static final Logger LOG = LoggerFactory.getLogger(AppConfig.class);

    // MongoDB configuration

    public static final String DB_NAME = "dime";

    public @Bean Mongo mongo() throws Exception {
	return new MongoClient("localhost");
    }
    
    public @Bean MongoTemplate mongoTemplate() throws Exception {
	return new MongoTemplate(mongo(), DB_NAME);
    }


    // Lucene configuration

    // @Value("#{appProperties['lucene.index_path']}")
    private String indexPath = "/home/mvsjober/var/dime-lucene";

    @Bean(name="analyzer")
    public Analyzer getAnalyzer() {
        return new StandardAnalyzer();
    }

    @Bean(name="fsDirectory")
    @DependsOn("analyzer")
    public FSDirectory getFSDirectory() throws IOException {
        return FSDirectory.open(Paths.get(indexPath)); //, new NativeFSLockFactory());
    }

    @Bean(name="indexWriter")
    @DependsOn("fsDirectory")
    public IndexWriter getIndexWriter() throws IOException {
        IndexWriterConfig iwc = new IndexWriterConfig(getAnalyzer());
        iwc.setOpenMode(OpenMode.CREATE_OR_APPEND);

	// Advice from Lucene example:
	// http://lucene.apache.org/core/5_3_0/demo/src-html/org/apache/lucene/demo/IndexFiles.html
	// Optional: for better indexing performance, if you
	// are indexing many documents, increase the RAM
	// buffer.  But if you do this, increase the max heap
	// size to the JVM (eg add -Xmx512m or -Xmx1g):
	//
	// iwc.setRAMBufferSizeMB(256.0);

        IndexWriter writer = new IndexWriter(getFSDirectory(), iwc);

	// NOTE: if you want to maximize search performance,
	// you can optionally call forceMerge here.  This can be
	// a terribly costly operation, so generally it's only
	// worth it when your index is relatively static (ie
	// you're done adding documents to it):
	//
	// writer.forceMerge(1);

	writer.commit();

        return writer;
    }

    @Bean(name="indexSearcher")
    @DependsOn("indexWriter")
    public IndexSearcher getIndexSearcher() throws IOException {
	try {
	    return new IndexSearcher(DirectoryReader.open(getFSDirectory()));
	} catch (IndexNotFoundException e) {
	    LOG.warn("No valid Lucene index found at " + indexPath);
	    return null;
	}
    }

    @Bean(name="queryParser")
    @DependsOn("analyzer")
    public StandardQueryParser getQueryParser() throws IOException {
        return new StandardQueryParser(getAnalyzer());
    }
}
