unset log
unset label
set title "WaniKani progress 2014" font "Verdana, 14"
set xdata time
set timefmt "%Y-%m-%d"
set format x "Week %W"
set xrange ["2014-01-12":"2014-12-31"]
set xtics rotate font "Tahoma, 10"
set y2tics font "Tahoma"
set ytics nomirror font "Tahoma"
set y2range [0:4000]
set yrange [0:50]
set ylabel "Level" font "Verdana"
set grid y2tics xtics
set key outside below font "Verdana"
set terminal pngcairo dashed size 1000, 700
set output "wk_progress.png"

plot \
"wkstats_plot.tmp" using 1:3 with linespoints lc rgb '#00a0f1' lt 1 lw 2 pt 0 ps 0 axes x1y2 title "Total Radicals",\
"wkstats_plot.tmp" using 1:2 with linespoints lc rgb '#00a0f1' lt 2 lw 2 pt 0 ps 0 axes x1y2 title "Burned Radicals",\
"wkstats_plot.tmp" using 1:5 with linespoints lc rgb '#f100a0' lt 1 lw 2 pt 0 ps 0 axes x1y2 title "Total Kanji",\
"wkstats_plot.tmp" using 1:4 with linespoints lc rgb '#f100a0' lt 2 lw 2 pt 0 ps 0 axes x1y2 title "Burned Kanij",\
"wkstats_plot.tmp" using 1:7 with linespoints lc rgb '#a000f1' lt 1 lw 2 pt 0 ps 0 axes x1y2 title "Total Vocabulary",\
"wkstats_plot.tmp" using 1:6 with linespoints lc rgb '#a000f1' lt 2 lw 2 pt 0 ps 0 axes x1y2 title "Burned Vocabulary",\
"wkstats_plot.tmp" using 1:8 with linespoints lc rgb '#000000' lt 1 lw 2 pt 0 ps 0 axes x1y1 title "Level"
