using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
// depends on AngleSharp
using AngleSharp;
using AngleSharp.Dom;
using AngleSharp.Html.Dom;
using AngleSharp.Html.Parser;

/*
Extract announcements data from html pages into csv
 */

namespace html_extractor
{
    class Program
    {
        static void Main(string[] args)
        {
            var p = new HtmlParser();
            using (StreamWriter fout = new StreamWriter(new BufferedStream(new FileStream("announce.csv", FileMode.Create))))
            {
                for (int i = 0; i <= 250; ++i)
                {
                    string path = $"dailyfx/{i}.html";

                    using (var input = new FileStream(path, FileMode.Open))
                    {
                        IHtmlDocument doc = p.ParseDocument(input);

                        foreach (IElement table in doc.GetElementsByTagName("table"))
                        {
                            if (table.Id == null || !table.Id.StartsWith("daily")) continue;

                            foreach (IElement evt in table.GetElementsByClassName("event"))
                            {
                                string[] cols = new string[]
                                {
                                    evt.Children[1].TextContent,
                                    evt.Children[2].FirstElementChild.GetAttribute("data-filter"),
                                    evt.Children[3].LastChild.TextContent,
                                    evt.Children[4].FirstElementChild.TextContent,
                                    evt.Children[5].TextContent,
                                    evt.Children[6].TextContent,
                                    evt.Children[7].TextContent,
                                };
                                
                                // write out a properly escaped csv line
                                fout.WriteLine(String.Join(",", cols.Select(str => $"\"{str.Trim().Replace("\"","\"\"")}\"")));
                            }
                        }
                    }
                }
            }
        }
    }
}
