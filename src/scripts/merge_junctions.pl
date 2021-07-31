#!/usr/bin/perl -w
use strict;
my %junctions;
foreach my $file (@ARGV){
    print STDERR "$file";
    open(IN,$file) or die;
    my $p = scalar keys %junctions;
    while (<IN>) {
        chomp;
        my @line = split(/\t/);
        my $key = join("\t",@line[0..2]);
        if (defined $junctions{$key}) {
            $junctions{$key}{u} += $line[6];
            $junctions{$key}{m} += $line[7];
            $junctions{$key}{o} = $line[8] > $junctions{$key}{o} ? $line[8] : $junctions{$key}{o};
        }else{
            $junctions{$key}{s} = $line[3];
            $junctions{$key}{i} = $line[4];
            $junctions{$key}{a} = $line[5];
            $junctions{$key}{u} = $line[6];
            $junctions{$key}{m} = $line[7];
            $junctions{$key}{o} = $line[8];
        }
        
    }
    print STDERR " New junctions: " ,  (scalar keys %junctions) - $p , "\n";
    close IN;
}

foreach my $key (keys %junctions){
    print join("\t",$key,$junctions{$key}{s},$junctions{$key}{i},$junctions{$key}{a},$junctions{$key}{u},$junctions{$key}{m},$junctions{$key}{o}), "\n";
}
