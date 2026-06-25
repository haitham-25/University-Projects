import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class LanguageAnalysisDriver {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: LanguageAnalysisDriver <input path> <output path> [useCombiner: true/false]");
            System.exit(-1);
        }

        boolean useCombiner = true;
        if (args.length == 3) {
            useCombiner = Boolean.parseBoolean(args[2]);
        }

        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "Language-Based Partitioning Analysis" + (useCombiner ? " (With Combiner)" : " (No Combiner)"));
        
        job.setJarByClass(LanguageAnalysisDriver.class);
        job.setMapperClass(LanguageMapper.class);
        job.setReducerClass(LanguageReducer.class);
        job.setPartitionerClass(LanguagePartitioner.class);

        // Map Output: Key=Text(Language), Value=IntWritable(1)
        job.setMapOutputKeyClass(Text.class);
        job.setMapOutputValueClass(IntWritable.class);

        // Final Output: Key=Text(Language), Value=Text("Articles: count")
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        // Set Combiner if requested
        if (useCombiner) {
            job.setCombinerClass(LanguageCombiner.class);
            System.out.println("Running with Combiner...");
        } else {
            System.out.println("Running without Combiner...");
        }

        // Set number of reducers (e.g., one per major language)
        job.setNumReduceTasks(8);

        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        long startTime = System.currentTimeMillis();
        boolean success = job.waitForCompletion(true);
        long endTime = System.currentTimeMillis();

        if (success) {
            System.out.println("Job completed in: " + (endTime - startTime) + " ms");
            System.exit(0);
        } else {
            System.err.println("Job failed!");
            System.exit(1);
        }
    }
}
