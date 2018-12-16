
import argparse
import contextlib
import sys
import time
import random

from random import randint
import opentracing
import lightstep

# LightStep-provided data set.
a = ["engineering", "trace", "microservices", "span", "lightstep", "histogram", "tag"]


def quicksort(a):
    with opentracing.start_child_span(parent_span,
                    operation_name='quicksort/check_sorted') as child_span:
        child_span.log_event("What's left to sort?", payload={str(a)} )
        child_span.set_tag('step', 'check_sorted')
        if len(a)<=1:
            child_span.log_event("Nothing left to sort in this partition!", payload={str(a)} )
            return a
        sleep_dot()

    with opentracing.start_child_span(parent_span,
                    operation_name='quicksort/select_pivot') as child_span:
        child_span.set_tag('step', 'select_pivot')
        pivot = a[randint(0,len(a)-1)]
        smaller, equal, larger = [],[],[]
        child_span.log_event("Let's choose a new pivot string!", payload={pivot} )
        sleep_dot()

        for word in a:
            with opentracing.start_child_span(child_span,
                    operation_name='quicksort/sort_partition') as child_span:
                child_span.set_tag('step', 'sort_partition')
                child_span.log_event("Compare the pivot to elements in current partition.", payload={pivot, word} )
                if len(word) < len(pivot):
                    smaller.append(word)
                    child_span.set_tag('pivot', pivot)
                    child_span.log_event("Append to array of smaller strings.", payload={str(smaller)} )
                elif len(word) == len(pivot):
                    equal.append(word)
                    child_span.set_tag('pivot', pivot)
                    child_span.log_event("Append to array of equal strings.", payload={str(equal)} )
                else:
                    larger.append(word)
                    child_span.set_tag('pivot', pivot)
                    child_span.log_event("Append to array of larger strings.", payload={str(larger)} )
                # Print the pivot and each array to help visualize the recursion.
                print(pivot)
                print(smaller, equal, larger)
                sleep_dot()

        return quicksort(smaller)+equal+quicksort(larger)


def sleep_dot():
    time.sleep(0.05)
    sys.stdout.write('.')
    sys.stdout.flush()


def lightstep_tracer_from_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', help='Your LightStep access token.',
                        default='')
    parser.add_argument('--host', help='The LightStep reporting service host to contact.',
                        default='collector.lightstep.com')
    parser.add_argument('--port', help='The LightStep reporting service port.',
                        type=int, default=443)
    parser.add_argument('--use_tls', help='Whether to use TLS for reporting',
                        type=bool, default=True)
    parser.add_argument('--component_name', help='The LightStep component name',
                        default='quicksort')
    args = parser.parse_args()

    return lightstep.Tracer(
            component_name=args.component_name,
            access_token=args.token,
            collector_host=args.host,
            collector_port=args.port,
            verbosity=1,
            collector_encryption=('tls' if args.use_tls else 'none'))


if __name__ == '__main__':

    with lightstep_tracer_from_args() as tracer:
        opentracing.tracer = tracer

    print ("Unsorted:" ,a)

    with opentracing.tracer.start_span(operation_name='quicksort/parent') as parent_span:
        parent_span.set_tag('span_type', 'parent')
        sorted = quicksort(a)
        parent_span.log_event("Quicksort result", payload={str(sorted)})

    print ("Sorted:" ,sorted)
