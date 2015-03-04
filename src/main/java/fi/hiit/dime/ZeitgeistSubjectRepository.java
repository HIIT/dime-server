package fi.hiit.dime;

import java.util.List;

import org.springframework.data.mongodb.repository.MongoRepository;

public interface ZeitgeistSubjectRepository extends MongoRepository<ZeitgeistSubject, String> {

    //public List<ZeitgeistSubject> findByActor(String actor);
}
