import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { describeFailure, type Failure } from "@/lib/services";

export function FailureNotice({ title, failure }: { title: string; failure: Failure }) {
  return (
    <Alert variant="destructive" className="bg-card">
      <AlertTitle className="text-base font-bold">{title}</AlertTitle>
      <AlertDescription className="text-base text-foreground">
        {describeFailure(failure)} Try again in a minute.
      </AlertDescription>
    </Alert>
  );
}
