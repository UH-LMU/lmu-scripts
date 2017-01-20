#!/usr/bin/perl
use strict;
use warnings;

use Data::Dumper qw(Dumper);
use DateTime;
use DateTime::Duration;
use DateTime::Format::DateParse;
use DateTime::Format::Duration;
use Text::CSV;


my $csv = Text::CSV->new({
  sep_char => ',',
  quote_char => '"',
  always_quote => 1,
  decode_utf8 => 1,
  binary => 1
 });

my $file = $ARGV[0] or die "Need to get CSV file on the command line\n";
my $file2 = $ARGV[1] or die "Need to get user permissions CSV file on the command line\n";

my %reservations;
my %permissions;
my $now = DateTime->now;

open(my $data, '<:encoding(utf8)', $file) or die "Could not open '$file' $!\n";
while (my $line = <$data>) {
  #chomp $line;
  #print $line;

  if ($csv->parse($line)) {

      my @fields = $csv->fields();
      my $user = $fields[6];
      my $resource = $fields[0];
      my $datetime = $fields[2];

      my ($date,$time) = split / /, $datetime;
      my ($day,$month,$year) = split /\//, $date;
      #print "found: ", $user, $resource, $datetime,$day,$month,$year, "\n";

      my $dt = DateTime->new(
            year       => $year,
            month      => $month,
            day        => $day,
            hour       => 0,
            minute     => 0,
            second     => 0,
            nanosecond => 0,
            time_zone  => 'Europe/Helsinki',
        );

      my $duration = $now - $dt;
      #my $format = DateTime::Format::Duration->new(pattern => '%Y years, %m months, %e days, %H hours, %M minutes, %S seconds');
      my $format = DateTime::Format::Duration->new(pattern => '%m');
      #my $format = DateTime::Format::Duration->new(pattern => '%e days');
      $reservations{$user}{$resource} = $format->format_duration($duration);

  } else {
      warn "Line could not be parsed: $line\n";
  }
}

#print Dumper \%reservations;
#print "----------------\n";

open(my $data2, '<:encoding(utf8)', $file2) or die "Could not open '$file2' $!\n";
while (my $line = <$data2>) {
  if ($csv->parse($line)) {

      my @fields = $csv->fields();
      my $user = shift @fields;
      $permissions{$user} = \@fields;
      # print "$user\n";
      # print Dumper \@permissions{$user};
      # print "---\n";

  } else {
      warn "Line could not be parsed (permissions): $line\n";
  }

}

#print Dumper \%permissions;
#print "----------------\n";


foreach my $user (sort keys %permissions) {
  foreach my $resource (@{$permissions{$user}}) {
    # print "$user, $resource";
    # print ", joo" if defined $reservations{$user}{$resource};
    # print "\n";
    $reservations{$user}{$resource} = "100"
      unless defined $reservations{$user}{$resource};
  }
}
foreach my $user (sort keys %reservations) {
    foreach my $resource (keys %{ $reservations{$user} }) {
        print "$user, $resource, $reservations{$user}{$resource}\n";
    }
    print ",,\n";
}
