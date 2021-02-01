import { Button, FormControl, Input, InputLabel } from "@material-ui/core";
import useForm from "../../lib/hooks/useForm";
import Pipeline from '../../lib/types/resource/pipeline';

export default function NewPipeline() {
  const { create, onChange } = useForm<Pipeline>({ service: 'pipeline' });
  return (
    <form noValidate autoComplete="off">
      <FormControl fullWidth>
        <InputLabel htmlFor="pipeline-name">Name</InputLabel>
        <Input id="pipeline-name" onChange={onChange("name")} />
      </FormControl>
      <Button variant="contained" color="primary" onClick={create}>
        Create
      </Button>
    </form>
  );
}
