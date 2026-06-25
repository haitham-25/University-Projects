import java.util.HashMap;
import org.apache.hadoop.conf.Configurable;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Partitioner;

/**
 * Custom Partitioner that distributes data by language.
 * Ensures each reducer processes exactly one language if possible.
 */
public class LanguagePartitioner extends Partitioner<Text, IntWritable> implements Configurable {
    private Configuration configuration;
    private HashMap<String, Integer> languageMap = new HashMap<>();

    @Override
    public void setConf(Configuration configuration) {
        this.configuration = configuration;
        // Pre-defined list of languages for deterministic partitioning
        String[] langs = {"Arabic", "English", "French", "Spanish", "German", "Chinese", "Russian", "Japanese"};
        for (int i = 0; i < langs.length; i++) {
            languageMap.put(langs[i], i);
        }
    }

    @Override
    public Configuration getConf() {
        return configuration;
    }

    @Override
    public int getPartition(Text key, IntWritable value, int numReduceTasks) {
        String lang = key.toString();
        Integer partitionId = languageMap.get(lang);
        
        // Handle unknown or unsupported LANGUAGES by sending them to partition 0
        if (partitionId == null) {
            return 0;
        }
        
        // Distribute within the available number of reducers
        return partitionId % numReduceTasks;
    }
}
