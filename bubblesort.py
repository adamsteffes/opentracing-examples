
import argparse
import sys
import time

import opentracing
import lightstep


a = ["engineering", "trace", "microservices", "span", "lightstep", "histogram", "tag"]

def bubblesort(a):
    swapped=True
    while swapped:
            swapped=False
            for i in range(1,len(a)):
                with opentracing.start_child_span(parent_span, operation_name='bubblesort/check_length') as child_span:
                    child_span.log_event("Compare length of index versus the previous element.")
                    child_span.set_tag('step', 'check_length')
                    sleep_dot()
                    if len(a[i-1]) > len(a[i]):
                        with opentracing.start_child_span(child_span, operation_name='bubblesort/swap_positions') as child_span:
                            child_span.log_event("Swap the index and the previous element.")
                            child_span.set_tag('step', 'swap_positions')
                            a[i],a[i-1] = a[i-1],a[i]
                            print(a)
                            swapped=True
                            sleep_dot()
    return a


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
                        default='bubblesort')
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

    with opentracing.tracer.start_span(operation_name='bubblesort/parent') as parent_span:
        parent_span.set_tag('span_type', 'parent')
        sorted = bubblesort(a)

    print ("Sorted:" ,sorted)
